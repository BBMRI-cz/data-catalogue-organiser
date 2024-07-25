import os
import uuid

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