import molgenis.client
import json
import os
import uuid
import pandas as pd
from manage_libraries import LibrariesManager

class Personal:

    def __init__(self, patient_dict):
        self.personalidentifier= patient_dict["ID"]
        self.phenotypicsex = patient_dict["sex"]
        self.genotypicsex = "Not asked (NASK, nullflavor)"
        self.countryofresidence = "Czechia"
        self.ancestry = ["Not asked (NASK, nullflavor)"]
        self.countryofbirth = "Czechia"
        self.yearofbirth = patient_dict["birth"].split("/")[1]
        self.inclusionstatus = "Not available (NAVU, nullflavor)"
        self.primaryaffiliatedinstitute = "Masaryk Memorial Cancer Institute"
        self.resourcesinotherinstitutes = ["Not available (NAVU, nullflavor)"]

class Clinical:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.clinicalidentifier = f"mmci_clinical_{uuid.UUID(int=int(sample['biopsy_number'].replace('/', '').replace('-', '')))}"
        self.belongstoperson = patient_dict["ID"]
        self.phenotype = ["NoInformation (NI, nullflavor)"]
        self.unobservedphenotype = ["NoInformation (NI, nullflavor)"]
        self.phenotypicdataavailable = ["NoInformation (NI, nullflavor)"]
        self.clinicaldiagnosis = self._adjust_diagnosis(sample["diagnosis"]) if sample["material"] != "genome" else None
        self.moleculardiagnosisgene = ["NoInformation (NI, nullflavor)"]
        self.ageatdiagnosis = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.ageatlastscreening = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.medication = ["NoInformation (NI, nullflavor)"]
        self.drugregimen = None
        self.familymembersaffected = ["NoInformation (NI, nullflavor)"]
        self.familymemberssequenced = ["NoInformation (NI, nullflavor)"]
        self.medicalhistory = ["NoInformation (NI, nullflavor)"]

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
        self.materialidentifier = sample["sample_ID"]
        self.collectedfromperson = patient_dict["ID"]
        self.belongstodiagnosis = f"mmci_clinical_{uuid.UUID(int=int(sample['biopsy_number'].replace('/', '').replace('-', '')))}"
        self.samplingtimestamp = sample["cut_time"] if sample["material"] == "tissue" else sample["taking_date"]
        self.registrationtimestamp = sample["freeze_time"] if sample["material"] == "tissue" else sample["taking_date"]
        self.samplingprotocol = "NoInformation (NI, nullflavor)"
        self.samplingprotocoldeviation = "NoInformation (NI, nullflavor)"
        self.reasonforsamplingprotocoldeviation = "NoInformation (NI, nullflavor)"
        self.biospecimentype = sample_dict["bioSpeciType"]
        self.anatomicalsource = "NoInformation (NI, nullflavor)"
        self.pathologicalstate = sample_dict["pathoState"]
        self.storageconditions = sample_dict["storCond"]
        self.percentagetumourcells = None
        self.physicallocation = "MMCI Biobank"
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
        self.sampleprepidentifier = sample["pseudo_ID"].replace("predictive", "sampleprep")
        self.belongstomaterial = sample["sample_ID"]
        lib_data = LibrariesManager(libraries_path, sample_sheet, run_path, sample["pseudo_ID"]).get_data_from_libraries()
        
        if lib_data:
            self.inputamount= lib_data["input_amount"]
            self.librarypreparationkit= lib_data["library_prep_kit"]
            self.pcrfree= lib_data["pca_free"]
            self.targetenrichmentkit=  lib_data["target_enrichment_kid"]
            self.umispresent= lib_data["umi_present"]
            self.intendedinsertsize= lib_data["intended_insert_size"]
            self.intendedreadlength= lib_data["intended_read_length"]
            self.genes = lib_data["genes"]

class Sequencing:
    def __init__(self, patient_dict, sample_dict, run_metadata_dict):
        sample = patient_dict["samples"][0]
        self.sequencingidentifier = sample["pseudo_ID"]
        self.belongstosample = sample["pseudo_ID"].replace("predictive", "sampleprep")
        self.sequencingdate = run_metadata_dict["seqDate"]
        self.sequencingplatform = run_metadata_dict["seqPlatform"]
        self.sequencinginstrumentmodel = run_metadata_dict["seqModel"]
        self.sequencingmethod = run_metadata_dict["seqMethod"]
        self.averagereaddepth = sample_dict["avReadDepth"]
        self.observedreadlength = sample_dict["obsReadLength"]
        self.percentageq30 = run_metadata_dict["percentageQ30"].replace("%", "")
        self.otherqualitymetrics = f"ClusterPF: {run_metadata_dict['clusterPF']}, numLanes: {run_metadata_dict['numLanes']}, flowcellID: {run_metadata_dict['flowcellID']}"

class Analysis:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.analysisidentifier = sample["pseudo_ID"].replace("predictive", "analysis")
        self.belongstosequencing = sample["pseudo_ID"]
        self.physicaldatalocation = "Masaryk Memorial Cancer Istitute"
        self.abstractdatalocation = "Sensitive Cloud Institute of Computer Science"
        self.dataformatsstored = ["BAM", "VCF"]
        self.referencegenomeused = "NoInformation (NI, nullflavor)"
        self.bioinformaticprotocolused = "NextGENe"

class IndividualConsent:
    def __init__(self, patient_dict):
        self.individualconsentidentifier = patient_dict["ID"].replace("patient", "consent")
        self.personconsenting = patient_dict["ID"]
        self.consentformused = "mmci_consentform_"
        self.collectedby= "Masaryk Memorial Cancer Instutite"
        self.signingdate = ""
        self.validfrom = ""
        self.validuntil = ""
        self.representedby = "patient"
        self.datausepermissions = "general research use"
        self.datatausespecification = ""
        self.allowrecontacting = ""

class MolgenisImporter:

    def __init__(self, run_path, wsi_path, libraries_path, login, password):
        self.session = molgenis.client.Session("https://data.bbmri.cz")
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
            personal_ids = [val["personalidentifier"] for val in self.session.get('fair-genomes_personal')]
            if personal.personalidentifier not in personal_ids:
                self._add_data(personal ,'fair-genomes_personal')

            clinical = Clinical(clinical_info_file)
            clinical_ids = [val["clinicalidentifier"] for val in self.session.get('fair-genomes_clinical')]
            if clinical.clinicalidentifier not in clinical_ids:
                self._add_data(clinical, 'fair-genomes_clinical')

            material = Material(self.wsi_path, clinical_info_file, sample_metadata_file)
            material_ids = [val["materialidentifier"] for val in self.session.get('fair-genomes_material')]
            if material.materialidentifier not in material_ids:
                self._add_data(material, 'fair-genomes_material')

            sample_preparation = SamplePreparation(self.run_path, self.libraries_path, self.sample_sheet_path, clinical_info_file)
            sample_prep_ids = [val["sampleprepidentifier"] for val in self.session.get('fair-genomes_samplepreparation')]
            if sample_preparation.sampleprepidentifier not in sample_prep_ids:
                self._add_data(sample_preparation, 'fair-genomes_samplepreparation')

            sequencing = Sequencing(clinical_info_file, sample_metadata_file, self.run_metadata)
            sequencing_ids = [val["sequencingidentifier"] for val in self.session.get('fair-genomes_sequencing')]
            if sequencing.sequencingidentifier not in sequencing_ids:
                self._add_data(sequencing, 'fair-genomes_sequencing')

            analysis = Analysis(clinical_info_file)
            analysis_ids = [val["analysisidentifier"] for val in self.session.get("fair-genomes_analysis")]
            if analysis.analysisidentifier not in analysis_ids:
                self._add_data(analysis, 'fair-genomes_analysis')

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
    