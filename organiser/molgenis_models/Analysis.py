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