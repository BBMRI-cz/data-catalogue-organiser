import uuid

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