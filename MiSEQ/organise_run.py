import os
import pandas as pd
import argparse
from pathlib import Path
import shutil
import json

class RunOrganiser:

    def __init__(self, path_to_pseudonymized_runs_folder, name_of_single_run, path_to_oragnised_storage, path_to_patients):
        self.pseudo_run = path_to_pseudonymized_runs_folder
        self.file = name_of_single_run
        self.organised_runs = path_to_oragnised_storage
        self.organised_patients = path_to_patients

    def __call__(self):
        return self.organise_run()

    def organise_run(self):
        y, machine, run_number = self.split_file_to_parts(self.file)
        run_path = os.path.join(self.organised_runs, y, machine, run_number)
        Path(run_path).mkdir(parents=True, exist_ok=True)
        self.create_sample_dirs(run_path, self.file)
        self.create_general_file(run_path, self.file)
        self.create_patient_files(self.file)
        return os.path.join(y, machine, run_number, self.file)

    def split_file_to_parts(self, filename):
        splitted_filename = filename.split("_")
        year = splitted_filename[0][:2]
        if splitted_filename[1][0] == "M":
            machine = "MiSEQ"
            run_number = splitted_filename[1][1:]
        else:
            machine = "NextSEQ"
            run_number = splitted_filename[1][2:]
        
        return f"20{year}", machine, run_number

    def create_sample_dirs(self, run_path, filename):
        sample_sheet_path = os.path.join(self.pseudo_run, filename, "SampleSheet.csv")
        pseudo_numbers = self.get_pseudo_numbers(sample_sheet_path)
        run_path = os.path.join(run_path, filename, "Samples")
        Path(run_path).mkdir(parents=True, exist_ok=True)

        for pseudo_number in pseudo_numbers:
            new_pseudo_folder = os.path.join(run_path, pseudo_number)
            Path(new_pseudo_folder).mkdir(parents=True, exist_ok=True)
            self.collect_data_for_pseudo_number(filename, new_pseudo_folder, pseudo_number)

    def create_general_file(self, new_file_path, file):
        general_file_path = os.path.join(self.pseudo_run, file)
        new_general_file_path = os.path.join(new_file_path, file)
        Path(new_general_file_path).mkdir(parents=True, exist_ok=True)

        run_parameters = os.path.join(general_file_path, "runParameters.xml")
        new_run_parameters = os.path.join(new_general_file_path, "runParameters.xml")
        shutil.copy2(run_parameters, new_run_parameters)

        run_info = os.path.join(general_file_path, "RunInfo.xml")
        new_run_info = os.path.join(new_general_file_path, "RunInfo.xml")
        shutil.copy2(run_info, new_run_info)

        completed_job = os.path.join(general_file_path, "CompletedJobInfo.xml")
        new_completed_job = os.path.join(new_general_file_path, "CompletedJobInfo.xml")
        shutil.copy2(completed_job, new_completed_job)

        generate_statistics = os.path.join(general_file_path, "GenerateFASTQRunStatistics.xml")
        new_generate_statistics = os.path.join(new_general_file_path, "GenerateFASTQRunStatistic.xml")
        shutil.copy2(generate_statistics, new_generate_statistics)

        analysis_log  = os.path.join(general_file_path, "AnalysisLog.txt")
        new_analysis_log = os.path.join(new_general_file_path, "AnalysisLog.txt")
        shutil.copy2(analysis_log, new_analysis_log)

        data_intensities_basecalls_alignments = os.path.join(general_file_path, "Data", "Intensities", "BaseCalls", "Alignment")
        new_data_intenstisities_basecalls_alignment = os.path.join(new_general_file_path, "Data", "Intensities", "Basecalls")
        Path(new_data_intenstisities_basecalls_alignment).mkdir(parents=True, exist_ok=True)
        shutil.copytree(data_intensities_basecalls_alignments, os.path.join(new_data_intenstisities_basecalls_alignment, "Alignment"))

        data_inter_op = os.path.join(general_file_path, "InterOp")
        new_data_inter_op = os.path.join(new_general_file_path, "InterOp")
        shutil.copytree(data_inter_op, new_data_inter_op)

        data_logs = os.path.join(general_file_path, "Logs")
        new_data_logs = os.path.join(new_general_file_path, "Logs")
        shutil.copytree(data_logs, new_data_logs)

        data_config = os.path.join(general_file_path, "Config")
        new_data_config = os.path.join(new_general_file_path, "Config")
        shutil.copytree(data_config, new_data_config)

        sample_sheet = os.path.join(general_file_path, "SampleSheet.csv")
        new_sample_sheet = os.path.join(new_general_file_path, "SampleSheet.csv")
        shutil.copy2(sample_sheet, new_sample_sheet)

        clinical_info = os.path.join(general_file_path, "clinical_info.json")
        new_clinical_info = os.path.join(new_general_file_path, "clinical_info.json")
        shutil.copy2(clinical_info, new_clinical_info)

        catalog_info_per_pac = os.path.join(general_file_path, "catalog_info_per_pred_number")
        new_catalog_info_per_pac = os.path.join(new_general_file_path, "catalog_info_per_pred_number")
        shutil.copytree(catalog_info_per_pac, new_catalog_info_per_pac)

    def get_pseudo_numbers(self, sample_sheet_path):
        df = pd.read_csv(sample_sheet_path, delimiter=",", )
        sample_list_header = df["[Header]"].to_list()
        id = sample_list_header.index("Sample_ID") + 1
        pseudo_numbers = sample_list_header[id:]

        return pseudo_numbers

    def collect_data_for_pseudo_number(self, filename, new_folder, pseudo_number):
        basecalls = os.path.join(self.pseudo_run, filename, "Data", "Intensities", "BaseCalls")
        new_fastq_folder = os.path.join(new_folder, "FASTQ")
        Path(new_fastq_folder).mkdir(parents=True, exist_ok=True)

        for file in os.listdir(basecalls):
            if pseudo_number in file:
                shutil.copy2(os.path.join(basecalls, file), os.path.join(new_fastq_folder, file))

        #analysis
        analysis = os.path.join(self.pseudo_run, filename, "Analysis")
        new_analysis = os.path.join(new_folder, "Analysis", "Reports")
        Path(new_analysis).mkdir(parents=True, exist_ok=True)

        self.get_bams(os.path.join(analysis, "BAM"), new_analysis, pseudo_number)

        for file in os.listdir(analysis):
            if "_Output" in file and pseudo_number in file:
                modified_pseudo_number = file.replace("_Output", "")
                if os.path.exists(os.path.join(analysis, file, modified_pseudo_number)):
                    self.get_outputs(os.path.join(analysis, file, modified_pseudo_number), new_analysis, modified_pseudo_number)
                elif os.path.exists(os.path.join(analysis, file, "sens")):
                    self.get_outputs(os.path.join(analysis, file, "sens"), new_analysis, modified_pseudo_number)
                if os.path.exists(os.path.join(analysis, file, "Preprocessed")):
                    self.get_convert(os.path.join(analysis, file, "Preprocessed"), new_analysis)

        #metadata
    def get_bams(self, path, new_path, pseudo_number):
        for file in os.listdir(path):
            if pseudo_number in file and ".bam" in file:
                shutil.copy2(os.path.join(path, file), os.path.join(new_path, file))

    def get_outputs(self, path, new_path, pseudo_number):
        parameters = os.path.join(path, f"{pseudo_number}_Parameters.txt")
        stat_info = os.path.join(path, f"{pseudo_number}_StatInfo.txt")
        bamconversion = os.path.join(path, "bamconversion.log")

        new_parameters = os.path.join(new_path, f"{pseudo_number}_Parameters.txt")
        new_stat_info = os.path.join(new_path, f"{pseudo_number}_StatInfo.txt")
        new_bamconversion = os.path.join(new_path, "bamconversion.log")

        if os.path.exists(parameters):
            shutil.copy2(parameters, new_parameters)
        if os.path.exists(stat_info):
            shutil.copy2(stat_info, new_stat_info)
        if os.path.exists(bamconversion):
            shutil.copy2(bamconversion, new_bamconversion)

    def get_convert(self, path, new_path):
        for file in os.listdir(path):
            if file.endswith("convert.log") or file.endswith("converted.fasta"):
                shutil.copy2(os.path.join(path, file), os.path.join(new_path, file))

            if file.endswith("RemoveDuplicates.log"):
                shutil.copy2(os.path.join(path, file), os.path.join(new_path, file))

    def create_patient_files(self,  run_file):
        clinical_info_path = os.path.join(self.pseudo_run, run_file, "clinical_info.json")

        with open(clinical_info_path) as json_file:
            data = json.load(json_file)

        if len(data["clinical_data"]) == 0:
            return None

        for patient in data["clinical_data"]:
            year = patient["birth"].replace("--", "").split("/")[1]
            patient_folder = os.path.join(self.organised_patients, year, f"{patient['ID']}")
            Path(patient_folder).mkdir(parents=True, exist_ok=True)
            patient_metadata_file = os.path.join(patient_folder, "patient_metadata.json")
            with open(patient_metadata_file, "w") as f:
                json.dump(patient, f, indent=4)