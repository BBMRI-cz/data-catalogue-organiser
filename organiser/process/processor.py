import os
import shutil
import logging
import sys
from datetime import datetime
import pandas as pd
from organiser.run_organisers.nextseq_organise_run import NextSeqRunOrganiser
from organiser.run_organisers.old_miseq_organise_run import OldMiseqRunOrganiser
from organiser.run_organisers.new_miseq_organise_run import NewMiseqRunOrganiser
from organiser.run_organisers.organise_run import OrganiseRun
from organiser.helpers.file_helpers import create_dictionary_if_not_exist


class Processor:
    def __init__(self, pseudnymized_runs_folder, folder_for_organised_files, patient_folder):
        self.psedunymized_runs_folder = pseudnymized_runs_folder
        self.organised_files_folder = folder_for_organised_files
        self.patient_folder = patient_folder

    def process_runs(self):
        self._create_important_folders_if_not_exist()
        logging.basicConfig(filename=os.path.join(self.organised_files_folder, "logs",
                                                  datetime.now().strftime('%d_%m_%Y-%H_%M.log')),
                            encoding='utf-8',
                            level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        for run in os.listdir(self.psedunymized_runs_folder):
            if run in ["backups", "logs", "errors"]:
                continue
            logging.info(f"Organising: {run}")
            organiser = self._get_correct_organiser(run)
            self._try_organise_run(run, organiser)

        logging.info("Done!")

    def _try_organise_run(self, run, organiser) -> bool:
        try:
            organiser.organise_run()
            shutil.move(os.path.join(self.psedunymized_runs_folder, run),
                        os.path.join(self.organised_files_folder, "backups", run))
            logging.info(f"Run {run} moved into backups")
            return True
        except FileNotFoundError as e:
            logging.exception(f"Run {run} is missing some data\nError:\n{e}")
            shutil.move(os.path.join(self.psedunymized_runs_folder, run),
                        os.path.join(self.organised_files_folder, "errors", run))
            return False
        except Exception as e:
            logging.exception(f"Unknown error: {e}")
            shutil.move(os.path.join(self.psedunymized_runs_folder, run),
                        os.path.join(self.organised_files_folder, "errors", run))
            return False

    def _create_important_folders_if_not_exist(self):
        create_dictionary_if_not_exist(os.path.join(self.organised_files_folder, "logs"))
        create_dictionary_if_not_exist(os.path.join(self.organised_files_folder, "backups"))
        create_dictionary_if_not_exist(os.path.join(self.organised_files_folder, "errors"))

    def _get_correct_organiser(self, run_path) -> OrganiseRun:
        full_run_path = os.path.join(self.psedunymized_runs_folder, run_path)

        if "Alignment_1" in os.listdir(full_run_path) or "SoftwareVersionsFile" in os.listdir(full_run_path):
            logging.info(f"{run_path} processed as New Miseq")
            return NewMiseqRunOrganiser(self.psedunymized_runs_folder, run_path,
                                        self.organised_files_folder, self.patient_folder)
        elif self._is_run_nextseq(full_run_path):
            logging.info(f"{run_path} processed as NextSeq")
            return NextSeqRunOrganiser(self.psedunymized_runs_folder, run_path,
                                       self.organised_files_folder, self.patient_folder)
        else:
            logging.info(f"{run_path} processed as Old Miseq")
            return OldMiseqRunOrganiser(self.psedunymized_runs_folder, run_path,
                                        self.organised_files_folder, self.patient_folder)

    def _is_run_nextseq(self, full_run_path) -> bool:
        sample_sheet_path = os.path.join(full_run_path, "SampleSheet.csv")
        df = pd.read_csv(sample_sheet_path, delimiter=",",
                         names=["[Header]", "Unnamed: 1", "Unnamed: 2", "Unnamed: 3", "Unnamed: 4",
                                "Unnamed: 5", "Unnamed: 6", "Unnamed: 7", "Unnamed: 8", "Unnamed: 9"])

        application_list = df[df["[Header]"] == "Application"]["Unnamed: 1"].tolist()
        if not application_list:
            return False
        application_value = application_list[0]
        return application_value.startswith("NextSeq")
