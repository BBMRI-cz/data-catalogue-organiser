import json
import sys
import re
import os

class SampleInfoMMCI:

    def __init__(self):
        self.idSample: str = ''
        self.collFromPerson: str = ''
        self.belToDiag: str = ''
        self.bioSpeciType: str = ''
        self.pathoState: str = ''
        self.storCond: str = ''
        self.wsiAvailability: bool = False
        self.radioDataAvailability: bool = False
        self.avReadDepth: str = ''
        self.obsReadLength: str = ''

class CollectSampleMetadata:

    def __init__(self, run_path, sample_stat_info_path, catalog_info_path):
        self.sample_info = SampleInfoMMCI()
        self.run_path = run_path
        self.sample_path = sample_stat_info_path
        self.clinical_data_path = catalog_info_path

    def __call__(self):
        sample_id = os.path.basename(self.sample_path).replace("_StatInfo.txt", "")
        metadata = self._find_sample_metadata(sample_id)
        if not os.path.exists(os.path.join(self.run_path, "sample_metadata")):
            os.mkdir(os.path.join(self.run_path, "sample_metadata"))
        with open(os.path.join(self.run_path, "sample_metadata" ,f'{sample_id}.json'), "w+") as outfile:
            json.dump(metadata, outfile, indent=4)

    def _find_sample_metadata(self, sample_id):
        self._find_data_in_statinfo(self.sample_path)
        self._find_data_in_clinical_info(self.clinical_data_path, sample_id)
        jsonStr = self.sample_info.__dict__
        return jsonStr

    def _find_data_in_statinfo(self, txt_statInfo):
        with open(txt_statInfo, 'r', encoding='utf-8', errors="ignore") as f:
            for line in f:
                match1 = re.search(r'Average Read Length: ([\d]+)', line)
                if match1:
                    self.sample_info.obsReadLength = match1.group(1)
                match2 = re.search(r'Average Coverage: ([\d]+)', line)
                if match2:
                    self.sample_info.avReadDepth = match2.group(1)

    def _find_data_in_clinical_info(self, json_clinical_data, sample_id):
        if os.path.exists(os.path.join(json_clinical_data, f"{sample_id}.json")):
            with open(os.path.join(json_clinical_data, f"{sample_id}.json"), encoding='utf-8') as json_file:
                data = json.load(json_file)
                    
            self.sample_info.idSample = data.get('samples')[0].get('pseudo_ID')
            self.sample_info.collFromPerson = data.get('ID')
            self.sample_info.belToDiag = self.sample_info.collFromPerson[:5] + "clinical" + self.sample_info.collFromPerson[12:]
            material = data.get('samples')[0].get('material_type')
            self.sample_info.pathoState = "NoInformation (NI, nullflavor)"
            if material == "4" or material == "54":
                self.sample_info.pathoState = "Normal"
            if material == "1" or material == "2" or material == "3" or material == "5" or material == "53" or material == "55" or material == "56":
                self.sample_info.pathoState = "Tumor"
            if material == "1" or material == "2" or material == "3" or material == "4" or material == "5":
                self.sample_info.bioSpeciType = "Frozen Tissue"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to <-135°C"
            if material == "53" or material == "54" or material == "55" or material == "56":
                self.sample_info.bioSpeciType = "Cryopreserved Tissue"
            if material == "7":
                self.sample_info.bioSpeciType = "Cell Pellet"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to <-135°C"
            if material == "C" or material == "K" or material == "L" or material == "PD" or material == "SD" or material == "T":
                self.sample_info.bioSpeciType = "Serum or Plasma"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to <-135°C"
            if material == "gD":
                self.sample_info.bioSpeciType = "Blood DNA"
                self.sample_info.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
            if material == "PK":
                self.sample_info.bioSpeciType = "Peripheral Blood"
                self.sample_info.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
            if material == "PR":
                self.sample_info.bioSpeciType = "Tumor Cell Line"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to <-135°C"