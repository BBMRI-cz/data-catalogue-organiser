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
        self.OtherQualityMetrics = f"ClusterPF: {run_metadata_dict['clusterPF']}"