from organise_run import RunOrganiser
from miseq_run_metadata import CollectRunMetadata
from miseq_sample_metadata import CollectSampleMetadata
from import_metadata import MolgenisImporter
import argparse
import os
import shutil
import logging
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="Organiser",
    description="Organise pseudonymized runs into a specifed output folder \n. It is important to use full paths")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to sequencing run path that will be pseudonymized")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")
    parser.add_argument("-w", "--wsi", type=str, required=True, help="Path to a WSI folder")
    parser.add_argument("-d", "--documents", type=str, required=True, help="Path to a libraries document")
    args = parser.parse_args()

    if not os.path.exists(os.path.join(args.output, "logs")):
        os.mkdir(os.path.join(args.output, "logs"))

    logging.basicConfig(filename=os.path.join(args.output,"logs", datetime.now().strftime('%d_%m_%Y-%H_%M.log')), 
                        encoding='utf-8', level=logging.INFO)

    molgenis_login = os.environ['CATALOG-LOGIN']
    molgenis_password = os.environ['CATALOG-PASSWORD']
    if not os.path.exists(os.path.join(args.output, "backups")):
        os.mkdir(os.path.join(args.output, "backups"))
    if not os.path.exists(os.path.join(args.output,"errors")):
        os.mkdir(os.path.join(args.output,"errors"))

    for file in os.listdir(args.runs):
        upload_to_catalog = True
        logging.info(f"Organising: {file}")
        try:
            run_path = RunOrganiser(args.runs, file, args.output, args.patients)()
        except FileNotFoundError as e:
            logging.error(f"Run {file} is missing some data\nError:\n{e}")
            shutil.move(os.path.join(args.runs, file),os.path.join(args.output,"errors",file))
            continue

        logging.info("Collecting metadata...")
        upload_to_catalog = CollectRunMetadata(os.path.join(args.output, run_path))()
        catalog_info = os.path.join(args.output, run_path, "catalog_info_per_pred_number")
        for sample in os.listdir(catalog_info):
            sample = sample.replace(".json", "")
            sample_stat_info = os.path.join(os.path.join(args.output, run_path), "Samples", sample, "Analysis", "Reports", f"{sample}_StatInfo.txt")
            CollectSampleMetadata(os.path.join(args.output, run_path), sample_stat_info, catalog_info)()

 
        if upload_to_catalog:
            logging.info("Uploading data to catalog...")
            #importer = MolgenisImporter(os.path.join(args.output, run_path) , args.wsi, args.documents, molgenis_login, molgenis_password)
            #importer()
            #del importer
        else:
            logging.warning("Some files are missing, no data uploaded to catalog!")

        shutil.move(os.path.join(args.runs, file), os.path.join(args.output, "backups" ,file))
        logging.info("File moved into backups")

    logging.info("Done!")