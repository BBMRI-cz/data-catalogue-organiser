from organise_run import RunOrganiser
from miseq_run_metadata import CollectRunMetadata
from miseq_sample_metadata import CollectSampleMetadata
from import_metadata import MolgenisImporter
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="Organiser",
    description="Organise pseudonymized runs into a specifed output folder \n. It is important to use full paths")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to sequencing run path that will be pseudonymized")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")
    parser.add_argument("-w", "--wsi", type=str, required=True, help="Path to a WSI folder")
    parser.add_argument("-d",  "--documents", type=str, required=True, help="Path to a libraries document")
    args = parser.parse_args()

    molgenis_login = os.environ['CATALOG-LOGIN']
    molgenis_password = os.environ['CATALOG-PASSWORD']

    for file in os.listdir(args.runs):
        print("Organising: ", file)
        run_path = RunOrganiser(args.runs, file, args.output, args.patients)()
        print("Collecting metadata...")
        CollectRunMetadata(os.path.join(args.output, run_path))()
        catalog_info = os.path.join(args.output, run_path, "catalog_info_per_pred_number")
        for sample in os.listdir(catalog_info):
            sample = sample.replace(".json", "")
            sample_stat_info = os.path.join(os.path.join(args.output, run_path), "Samples", sample, "Analysis", "Reports", f"{sample}_StatInfo.txt")
            CollectSampleMetadata(os.path.join(args.output, run_path), sample_stat_info, catalog_info)()

        print("Importing metadata to molgenis...")
        importer = MolgenisImporter(os.path.join(args.output, run_path) , args.wsi, args.documents, molgenis_login, molgenis_password)
        importer()
        del importer
    print("Done!")