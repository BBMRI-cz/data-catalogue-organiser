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