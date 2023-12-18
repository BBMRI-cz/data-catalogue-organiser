import molgenis.client
import json
import os
import uuid
import re
from manage_libraries import LibrariesManager

class Personal:

    def __init__(self, patient_dict):
        self.PersonalIdentifier= patient_dict["ID"]
        self.GenderIdentity = "Not asked (NASK, nullflavor)"
        self.GenderAtBirth = self._convert_gender_at_birth(patient_dict["sex"])
        self.GenotypicSex = self._convert_genotypic_sex(patient_dict["sex"])
        self.CountryOfResidence = "Czechia"
        self.Ancestry = ["Not asked (NASK, nullflavor)"]
        self.CountryOfBirth = "Czechia"
        self.YearOfBirth = patient_dict["birth"].split("/")[1]
        self.InclusionStatus = "Not available (NAVU, nullflavor)"
        self.PrimaryAffiliatedInstitute = "Masaryk Memorial Cancer Institute"
        self.ResourcesInOtherInstitutes = ["Not available (NAVU, nullflavor)"]

    def _convert_gender_at_birth(self, sex):
        if sex == "male":
            return "assigned male at birth"
        elif sex == "female":
            return "assigned female at birth"
        else:
            return "Asked but unkown (ASKU, nullflavor)"

    def _convert_genotypic_sex(self, sex):
        if sex == "male":
            return "XY Genotype"
        elif sex == "female":
            return "XX Genotype"
        else:
            return "Asked but unkown (ASKU, nullflavor)"

class Clinical:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.ClinicalIdentifier = f"mmci_clinical_{uuid.UUID(int=int(sample['biopsy_number'].replace('/', '').replace('-', '')))}"
        self.BelongsToPerson = patient_dict["ID"]
        self.Phenotype = ["NoInformation (NI, nullflavor)"]
        self.UnobservedPhenotype = ["NoInformation (NI, nullflavor)"]
        self.ClinicalDiagnosis = self._adjust_diagnosis(sample["diagnosis"]) if sample["material"] != "genome" else None
        self.MolecularDiagnosisGene = ["NoInformation (NI, nullflavor)"]
        self.AgeAtDiagnosis = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.AgeAtLastScreening = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.Medication = ["NoInformation (NI, nullflavor)"]
        self.MedicalHistory = ["NoInformation (NI, nullflavor)"]

    def _calculate_age_at_diagnosis(self, birth, sample):
        if sample["material"] == "tissue":
            return int(sample["freeze_time"].split("-")[0]) - int(birth)
        else:
            return int(sample["taking_date"].split("-")[0]) - int(birth)

    def _adjust_diagnosis(self, diagnosis):
        if len(diagnosis) == 4:
            return diagnosis[:3] + "." + diagnosis[3]
        return diagnosis

class Material:

    def __init__(self, wsi_path, patient_dict, sample_dict):
        sample =  patient_dict["samples"][0]
        self.MaterialIdentifier = sample["sample_ID"]
        self.CollectedFromPerson = patient_dict["ID"]
        self.BelongsToDiagnosis = f"mmci_clinical_{uuid.UUID(int=int(sample['biopsy_number'].replace('/', '').replace('-', '')))}"
        self.SamplingTimestamp = sample["cut_time"] if sample["material"] == "tissue" else sample["taking_date"]
        self.RegistrationTimestamp = sample["freeze_time"] if sample["material"] == "tissue" else sample["taking_date"]
        self.BiospecimenType = sample_dict["bioSpeciType"]
        self.PathologicalState = sample_dict["pathoState"]
        self.StorageConditions = sample_dict["storCond"]
        self.PercentageTumourCells = "NotAvailable (NA, nullflavor)"
        self.PhysicalLocation = "MMCI Bank of Biological Material"
        self.wholeslideimagesavailability = self._look_for_wsi(wsi_path, sample["biopsy_number"])
        self.radiotherapyimagesavailability	= False

    def _look_for_wsi(self, wsi_path, biopsy_number):
        wsi_folder, biopsy_start = self._make_path_from_biopsy_number(biopsy_number)

        if os.path.exists(os.path.join(wsi_path, wsi_folder)) and os.path.isdir(os.path.join(wsi_path, wsi_folder)):
            return any(str(folder).startswith(biopsy_start) for folder in os.listdir(os.path.join(wsi_path, wsi_folder)))
        return False

    def _make_path_from_biopsy_number(self, biopsy_number):
        year = biopsy_number.split("/")[0]
        remaining = biopsy_number.split("/")[1].split("-")[0].zfill(5)
        fixed_biopsy = f"{year}_{remaining}-{biopsy_number.split('/')[1].split('-')[1].zfill(2)}"

        return os.path.join(year, remaining[:2], remaining[2:]), fixed_biopsy

class SamplePreparation:

    def __init__(self, run_path, libraries_path, sample_sheet, patient_dict):
        sample = patient_dict["samples"][0]
        self.SampleprepIdentifier = sample["pseudo_ID"].replace("predictive", "sampleprep")
        self.BelongsToMaterial = sample["sample_ID"]
        lib_data = LibrariesManager(libraries_path, sample_sheet, run_path, sample["pseudo_ID"]).get_data_from_libraries()
        
        if lib_data:
            self.InputAmount= re.sub("[^0-9]", "", lib_data["input_amount"].split("-")[0]) if "-" in lib_data["input_amount"] else re.sub("[^0-9]", "", lib_data["input_amount"])
            self.LibraryPreparationKit= lib_data["library_prep_kit"]
            self.PcrFree= lib_data["pca_free"]
            self.TargetEnrichmentKit=  lib_data["target_enrichment_kid"]
            self.UmisPresent= lib_data["umi_present"]
            self.IntendedInsertSize= lib_data["intended_insert_size"]
            self.IntendedReadLength= lib_data["intended_read_length"]
            self.genes = lib_data["genes"]

class Sequencing:
    def __init__(self, patient_dict, sample_dict, run_metadata_dict):
        sample = patient_dict["samples"][0]
        self.SequencingIdentifier = sample["pseudo_ID"]
        self.BelongsToSamplePreparation = sample["pseudo_ID"].replace("predictive", "sampleprep")
        self.SequencingDate = run_metadata_dict["seqDate"]
        self.SequencingPlatform = run_metadata_dict["seqPlatform"]
        self.SequencingInstrumentModel = run_metadata_dict["seqModel"]
        self.SequencingMethod = run_metadata_dict["seqMethod"]
        self.MedianReadDepth = sample_dict["avReadDepth"]
        self.ObservedReadLength = sample_dict["obsReadLength"]
        self.PercentageQ30 = run_metadata_dict["percentageQ30"].replace("%", "")
        self.OtherQualityMetrics = f"ClusterPF: {run_metadata_dict['clusterPF']}, numLanes: {run_metadata_dict['numLanes']}, flowcellID: {run_metadata_dict['flowcellID']}"

class Analysis:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.AnalysisIdentifier = sample["pseudo_ID"].replace("predictive", "analysis")
        self.BelongsToSequencing = sample["pseudo_ID"]
        self.PhysicalDataLocation = "Masaryk Memorial Cancer Istitute"
        self.AbstractDataLocation = "Sensitive Cloud Institute of Computer Science"
        self.DataFormatsStored = ["BAM", "VCF"]
        self.ReferenceGenomeUsed = "GRCh37"
        self.BioinformaticProtocolUsed = "NextGENe"

class IndividualConsent:
    def __init__(self, patient_dict):
        sample =  patient_dict["samples"][0]
        self.IndividualConsentIdentifier = patient_dict["ID"].replace("patient", "consent")
        self.PersonConsenting = patient_dict["ID"]
        self.ConsentFormUsed = "mmci_consentform_1"
        self.CollectedBy= "Masaryk Memorial Cancer Institute"
        self.SigningDate = sample["freeze_time"] if sample["material"] == "tissue" else sample["taking_date"]
        self.RepresentedBy = "patient"
        self.DataUsePermissions = "general research use"

class MolgenisImporter:

    FAIR_PERSONAL = "fair-genomes_Personal"
    FAIR_CLINICAL = "fair-genomes_Clinical"
    FAIR_MATERIAL = "fair-genomes_Material"
    FAIR_SAMPLE_PREP = "fair-genomes_SamplePreparation"
    FAIR_SEQUENCING = "fair-genomes_Sequencing"
    FAIR_ANALYSIS = "fair-genomes_Analysis"
    FAIR_INDI_CONSENT = "fair-genomes_IndividualConsent"

    def __init__(self, run_path, wsi_path, libraries_path, login, password):
        self.session = molgenis.client.Session("https://data.bbmri.cz/api/")
        self.session.login(login, password)
        self.run_path =  run_path
        self.catalog_info_folder = os.path.join(run_path, "catalog_info_per_pred_number")
        self.samples_metadata_folder = os.path.join(run_path, "sample_metadata")
        self.wsi_path = wsi_path
        self.libraries_path = libraries_path
        self.sample_sheet_path = os.path.join(run_path,"SampleSheet.csv")
        with open(os.path.join(run_path,"run_metadata.json"), "r") as f:
            self.run_metadata = json.load(f)

    def __call__(self):
        for pred_number in os.listdir(self.catalog_info_folder):
            clinical_info_file = os.path.join(self.catalog_info_folder, pred_number)

            with open(clinical_info_file, "r") as f:
                clinical_info_file = json.load(f)

            sample_metadata_file = os.path.join(self.samples_metadata_folder, pred_number)
            with open(sample_metadata_file, "r") as f:
                sample_metadata_file = json.load(f)

            personal = Personal(clinical_info_file)
            personal_ids = [val["PersonalIdentifier"] for val in self.session.get(self.FAIR_PERSONAL)]
            if personal.PersonalIdentifier not in personal_ids:
                self._add_data(personal, self.FAIR_PERSONAL)

            consent = IndividualConsent(clinical_info_file)
            consent_ids = [val["IndividualConsentIdentifier"] for val in self.session.get(self.FAIR_INDI_CONSENT)]
            if consent.IndividualConsentIdentifier not in consent_ids:
                self._add_data(consent, self.FAIR_INDI_CONSENT)

            clinical = Clinical(clinical_info_file)
            clinical_ids = [val["ClinicalIdentifier"] for val in self.session.get(self.FAIR_CLINICAL)]
            if clinical.ClinicalIdentifier not in clinical_ids:
                self._add_data(clinical, self.FAIR_CLINICAL)

            material = Material(self.wsi_path, clinical_info_file, sample_metadata_file)
            material_ids = [val["MaterialIdentifier"] for val in self.session.get(self.FAIR_MATERIAL)]
            if material.MaterialIdentifier not in material_ids:
                self._add_data(material, self.FAIR_MATERIAL)

            sample_preparation = SamplePreparation(self.run_path, self.libraries_path, self.sample_sheet_path, clinical_info_file)
            sample_prep_ids = [val["SampleprepIdentifier"] for val in self.session.get(self.FAIR_SAMPLE_PREP)]
            if sample_preparation.SampleprepIdentifier not in sample_prep_ids:
                self._add_data(sample_preparation, self.FAIR_SAMPLE_PREP)

            sequencing = Sequencing(clinical_info_file, sample_metadata_file, self.run_metadata)
            sequencing_ids = [val["SequencingIdentifier"] for val in self.session.get(self.FAIR_SEQUENCING)]
            if sequencing.SequencingIdentifier not in sequencing_ids:
                self._add_data(sequencing, self.FAIR_SEQUENCING)

            analysis = Analysis(clinical_info_file)
            analysis_ids = [val["AnalysisIdentifier"] for val in self.session.get(self.FAIR_ANALYSIS)]
            if analysis.AnalysisIdentifier not in analysis_ids:
                self._add_data(analysis, self.FAIR_ANALYSIS)

    def __del__(self):
        self.session.logout()

    def _directorize(self, object):
        d = {}
        for key, value in object.__dict__.items():
            if value.__class__== tuple:
                d[key]= value[0]
            else:
                d[key] = value
        return d

    def _add_data(self, data, data_type):
        data_dict = self._directorize(data)
        datas = [data_dict]
        self.session.add_all(data_type, datas)
    