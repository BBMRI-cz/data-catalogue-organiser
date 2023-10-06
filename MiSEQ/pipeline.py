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
    parser.add_argument("-l", "--login", type=str, required=True, help="Login for the Molgenis Catalogue")
    parser.add_argument("-pw", "--password", type=str, required=True, help="Password for the Molgenis Catalogue")
    parser.add_argument("-d",  "--documents", type=str, required=True, help="Path to a libraries document")
    args = parser.parse_args()

    print(os.listdir(args.runs))
    print(os.listdir(args.patients))
    print(os.listdir(args.output))
    print(os.listdir(args.wsi))

    for file in os.listdir(args.runs):
        print(file)
        run_path = RunOrganiser(args.runs, file, args.output, args.patients)()
        CollectRunMetadata(os.path.join(args.output, run_path))()
        catalog_info = os.path.join(args.output, run_path, "catalog_info_per_pred_number")
        for sample in os.listdir(os.path.join(args.output, run_path, "catalog_info_per_pred_number")):
            sample = sample.replace(".json", "")
            sample_stat_info = os.path.join(os.path.join(args.output, run_path), "Samples", sample, "Analysis", "Reports", f"{sample}_StatInfo.txt")
            CollectSampleMetadata(os.path.join(args.output, run_path), sample_stat_info, catalog_info)()

        print("molgenis importer")
        importer = MolgenisImporter(os.path.join(args.output, run_path) , args.wsi, args.documents, args.login, args.password)
        importer()
        del importer