import molgenis.client
import json
import os

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
        self.participatesinstudy= None

class Clinical:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.clinicalidentifier = patient_dict["ID"].replace("patient", "clinical")
        self.belongstoperson = patient_dict["ID"]
        self.phenotype = ["NoInformation (NI, nullflavor)"]
        self.unobservedphenotype = ["NoInformation (NI, nullflavor)"]
        self.phenotypicdataavailable = ["NoInformation (NI, nullflavor)"]
        self.clinicaldiagnosis = self._adjust_diagnosis(sample["diagnosis"]) if sample["material"] != "genome" else None
        self.moleculardiagnosisgene = ["NoInformation (NI, nullflavor)"]
        self.moleculardiagnosisother = None
        self.ageatdiagnosis = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.ageatlastscreening = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.medication = ["NoInformation (NI, nullflavor)"]
        self.drugregimen = None
        self.familymembersaffected = ["NoInformation (NI, nullflavor)"]
        self.familymemberssequenced = ["NoInformation (NI, nullflavor)"]
        self.consanguinity = None
        self.medicalhistory = ["NoInformation (NI, nullflavor)"]
        self.ageofonset = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.firstcontact = None
        self.functioning = None
        self.materialusedindiagnosis = None

    def _calculate_age_at_diagnosis(self, birth, sample):
        if sample["material"] == "tissue":
            return int(sample["freeze_time"].split("-")[0]) - int(birth)
        else:
            return int(sample["taking_date"].split("-")[0]) - int(birth)

    def _adjust_diagnosis(self, diagnosis):
        if len(diagnosis) == 4:
            return diagnosis[:3]
        return diagnosis

class Material:

    def __init__(self, patient_dict, sample_dict):
        sample =  patient_dict["samples"][0]
        self.materialidentifier = sample["sample_ID"]
        self.collectedfromperson = patient_dict["ID"]
        self.belongstodiagnosis = patient_dict["ID"].replace("patient", "clinical")
        self.samplingtimestamp = sample["cut_time"]
        self.registrationtimestamp = sample["freeze_time"]
        self.samplingprotocol = "NoInformation (NI, nullflavor)"
        self.samplingprotocoldeviation = "NoInformation (NI, nullflavor)"
        self.reasonforsamplingprotocoldeviation = "NoInformation (NI, nullflavor)"
        self.biospecimentype = sample_dict["bioSpeciType"]
        self.anatomicalsource = "NoInformation (NI, nullflavor)"
        self.pathologicalstate = sample_dict["pathoState"]
        self.storageconditions = sample_dict["storCond"]
        self.expirationdate = None
        self.percentagetumourcells = None
        self.physicallocation = "FFPE blocks at Department of Oncological Pathology MMCI" #TODO
        self.derivedfrom = "NoInformation (NI, nullflavor)"
        self.wholeslideimagesavailability = False #TODO
        self.radiotherapyimagesavailability	= False #TODO

class SamplePreparation:

    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.sampleprepidentifier= sample["pseudo_ID"].replace("predictive", "sampleprep")
        self.belongstomaterial= sample["sample_ID"]

        # TODO wait for 'libraries_and_runs' to be final.
        self.inputamount= "15"
        self.librarypreparationkit="KAPA HyperPlus Kits by Roche"
        self.pcrfree="false"
        self.targetenrichmentkit="KAPA HyperPlus Kits by Roche"
        self.umispresent= "false"
        self.intendedinsertsize= "265"
        self.intendedreadlength= "282"
        # TODO

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
        self.observedinsertsize = None
        self.percentageq30 = run_metadata_dict["percentageQ30"].replace("%", "")
        self.percentagetr20 = None
        self.otherqualitymetrics = f"ClusterPF: {run_metadata_dict['clusterPF']}, numLanes: {run_metadata_dict['numLanes']}, flowcellID: {run_metadata_dict['flowcellID']}"

class Analysis:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.analysisidentifier = sample["pseudo_ID"].replace("predictive", "analysis")
        self.belongstosequencing = sample["pseudo_ID"]
        self.physicaldatalocation = "Masaryk Memorial Cancer Istitute"
        self.abstractdatalocation = "Sensitive Cloud Institute of Computer Science"
        self.dataformatsstored = [".fastq", "VCF"]
        self.algorithmsused = None #TODO
        self.referencegenomeused = "NoInformation (NI, nullflavor)"
        self.bioinformaticprotocolused = None
        self.bioinformaticprotocoldeviation = None
        self.reasonforbioinformaticprotocoldeviation = None
        self.wgsguidelinefollowed = None


class MolgenisImporter:

    def __init__(self, catalog_info, samples_metadata, run_metadata, login, password):
        self.session = molgenis.client.Session("https://data.bbmri.cz")
        self.session.login(login, password)
        self.catalog_info_folder = catalog_info
        self.samples_metadata_folder = samples_metadata
        with open(run_metadata, "r") as f:
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

            material = Material(clinical_info_file, sample_metadata_file)
            material_ids = [val["materialidentifier"] for val in self.session.get('fair-genomes_material')]
            if material.materialidentifier not in material_ids:
                self._add_data(material, 'fair-genomes_material')

            sample_preparation = SamplePreparation(clinical_info_file)
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
    