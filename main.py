import argparse
from organiser.process.processor import Processor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Organiser",
                                     description="Organise pseudonymized runs into a specifed output folder \n." +
                                                 " It is important to use full paths")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to pseudonymized runs")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")
    parser.add_argument("-l", "--log-dir", type=str, required=True, help="Path to a log folder")
    args = parser.parse_args()

    Processor(args.runs, args.output, args.patients, args.log_dir).process_runs()
