import molgenis.client
import json
import os


from molgenis_models.Analysis import Analysis
from molgenis_models.Clinical import Clinical
from molgenis_models.IndividualConsent import IndividualConsent
from molgenis_models.Material import Material
from molgenis_models.Personal import Personal
from molgenis_models.SamplePreparation import SamplePreparation
from molgenis_models.Sequencing import Sequencing

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
    