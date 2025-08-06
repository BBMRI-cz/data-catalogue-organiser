from organiser.helpers.file_helpers import copy_if_exists, copy_folder_if_exists
from organiser.run_organisers.old_miseq_organise_run import OldMiseqRunOrganiser
import os
from pathlib import Path

class NextSeqRunOrganiser(OldMiseqRunOrganiser):

    def organise_run(self):
        y = self._get_file_year()
        machine = "NextSeq"
        folder_for_run_path = os.path.join(self.organised_runs, y, machine)
        Path(folder_for_run_path).mkdir(parents=True, exist_ok=True)
        self._create_sample_dirs(folder_for_run_path)
        self._create_general_file(folder_for_run_path)
        self._create_patient_files_if_clinical_data_exist(folder_for_run_path)
        return os.path.join(folder_for_run_path, self.file)

    def _create_general_file(self, new_file_path):
        self._copy_important_files(os.path.join(self.pseudo_run, self.file), os.path.join(new_file_path, self.file))
        self._copy_important_folders(os.path.join(self.pseudo_run, self.file), os.path.join(new_file_path, self.file))


    def _copy_important_files(self, old_path, new_path):
        files_to_move = ["RunInfo.xml", "RunParameters.xml", "RunCompletionStatus.xml", "SampleSheet.csv"]

        for file in files_to_move:
            old_file_path = os.path.join(old_path, file)
            new_file_path = os.path.join(new_path, file)
            copy_if_exists(old_file_path, new_file_path)


    def _copy_important_folders(self, old_path, new_path):
        folders_path = [
            "catalog_info_per_pred_number"
        ]
        for folder in folders_path:
            old_folder_path = os.path.join(old_path, folder)
            new_folder_path = os.path.join(new_path, folder)
            copy_folder_if_exists(old_folder_path, new_folder_path)