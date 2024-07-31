import argparse
import os
import shutil
import logging
from datetime import datetime
from organiser.organise_run import RunOrganiser
from organiser.helpers.file_helpers import create_dictionary_if_not_exist


def _create_important_folders_if_not_exist(organisation_folder):
    create_dictionary_if_not_exist(os.path.join(organisation_folder, "logs"))
    create_dictionary_if_not_exist(os.path.join(organisation_folder, "backups"))
    create_dictionary_if_not_exist(os.path.join(organisation_folder, "errors"))


def run(path_to_runs_for_processing, path_to_organisation_folder, path_to_patient_organisation_folder):
    _create_important_folders_if_not_exist(path_to_organisation_folder)
    logging.basicConfig(filename=os.path.join(path_to_organisation_folder, "logs",
                                              datetime.now().strftime('%d_%m_%Y-%H_%M.log')),
                        encoding='utf-8',
                        level=logging.INFO)

    for file in os.listdir(path_to_runs_for_processing):
        logging.info(f"Organising: {file}")
        try:
            RunOrganiser(path_to_runs_for_processing, file,
                         path_to_organisation_folder, path_to_patient_organisation_folder)()
        except FileNotFoundError as e:
            logging.error(f"Run {file} is missing some data\nError:\n{e}")
            shutil.move(os.path.join(path_to_runs_for_processing, file),
                        os.path.join(path_to_organisation_folder, "errors", file))
            continue

        shutil.move(os.path.join(path_to_runs_for_processing, file),
                    os.path.join(path_to_organisation_folder, "backups", file))
        logging.info("File moved into backups")

    logging.info("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Organiser",
                                     description="Organise pseudonymized runs into a specifed output folder \n." +
                                                 " It is important to use full paths")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to pseudonymized runs")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")
    args = parser.parse_args()

    run(args.runs, args.output, args.patients)
