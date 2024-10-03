import os
from pathlib import Path

from organiser.helpers.file_helpers import copy_folder_if_exists, copy_if_exists
from .old_miseq_organise_run import OldMiseqRunOrganiser


class NewMiseqOrganiseRun(OldMiseqRunOrganiser):

    def organise_run(self):
        y = self._get_file_year()
        machine = "MiSEQ"
        folder_for_run_path = os.path.join(self.organised_runs, y, machine)
        Path(folder_for_run_path).mkdir(parents=True, exist_ok=True)
        self._create_sample_dirs(folder_for_run_path)
        self._create_general_file(folder_for_run_path)
        self._create_patient_files_if_clinical_data_exist()
        return os.path.join(folder_for_run_path, self.file)

    def _collect_data_for_pseudo_number(self, new_folder, pseudo_number):
        fastq_folder = os.path.join(self.pseudo_run, self.file, "Alignment_1", "Fastq")
        new_fastq_folder = os.path.join(new_folder, "FASTQ")
        Path(new_fastq_folder).mkdir(parents=True, exist_ok=True)

        for file in os.listdir(fastq_folder):
            if pseudo_number in file:
                copy_if_exists(os.path.join(fastq_folder, file),
                               os.path.join(new_fastq_folder, file))

        self._collect_analysis(new_folder, pseudo_number)

    def _create_general_file(self, new_file_path):
        general_file_path = os.path.join(self.pseudo_run, self.file)
        new_general_file_path = os.path.join(new_file_path, self.file)
        Path(new_general_file_path).mkdir(parents=True, exist_ok=True)

        self._copy_important_files(general_file_path, new_general_file_path)
        self._copy_important_folders(general_file_path, new_general_file_path)

    def _copy_important_files(self, old_path, new_path):
        files_to_move = [
            os.path.join("Alignment_1", "AnalysisLog.txt"),
            os.path.join("Alignment_1", "CompletedJobInfo.xml"),
            "RunParameters.xml",
            "RunInfo.xml",
            "SampleSheet.csv",
            "GenerateFASTQRunStatistics.xml"
        ]
        for file in files_to_move:
            base = os.path.basename(file)
            old_file_path = os.path.join(old_path, file)
            new_file_path = os.path.join(new_path, os.path.basename(file))
            copy_if_exists(old_file_path, new_file_path)

    def _copy_important_folders(self, old_path, new_path):
        folder_paths = [("Alignment_1", "Alignment"),
                        ("catalog_info_per_pred_number", "catalog_info_per_pred_number")]
        for old, new in folder_paths:
            old_folder_path = os.path.join(old_path, old)
            new_folder_path = os.path.join(new_path, new)
            copy_folder_if_exists(old_folder_path, new_folder_path)
