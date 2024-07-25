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