import pytest
import os
import shutil

from organiser.organise_run import RunOrganiser

FAKE_ALL_RUNS_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS")
FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs",
                                 "2020_M00000_0000_00000000-00000")


FAKE_RUN_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000")
FAKE_DESTINATION_FILES = os.path.join(os.path.dirname(__file__), "test_destination")
FAKE_PATIENT_FILES = os.path.join(os.path.dirname(__file__), "test_patients")


def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)
    os.mkdir(FAKE_DESTINATION_FILES)
    os.mkdir(FAKE_PATIENT_FILES)


@pytest.fixture()
def remove_analysis_from_pseudonymized_file():
    shutil.rmtree(os.path.join(FAKE_RUN_FOR_TESTING, "Analysis"))


def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_ALL_RUNS_FOR_TESTING)
    shutil.rmtree(FAKE_PATIENT_FILES)
    shutil.rmtree(FAKE_DESTINATION_FILES)


@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    request.addfinalizer(_remove_coppied_fake_run)


def test_folder_structure_correct():
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000"))


@pytest.mark.parametrize("id_part", ["1", "5", "9"])
def test_correct_files_fastq(id_part):
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    expected_run_folder = os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000")

    predictive_number = f"mmci_predictive_00000000-0000-0000-0000-00000000000{id_part}"

    assert os.path.exists(os.path.join(expected_run_folder, "Samples", predictive_number, "FASTQ",
                                       f"{predictive_number}_S{id_part}_L001_R1_001.fastq.gz"))
    assert os.path.exists(os.path.join(expected_run_folder, "Samples", predictive_number, "FASTQ",
                                       f"{predictive_number}_S{id_part}_L001_R2_001.fastq.gz"))


@pytest.mark.parametrize("id_part", ["1", "5", "9"])
def test_correct_analysis_files(id_part):
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    expected_run_folder = os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000")

    predictive_number = f"mmci_predictive_00000000-0000-0000-0000-00000000000{id_part}"

    files_in_analysis = os.listdir(os.path.join(expected_run_folder, "Samples",
                                                predictive_number, "Analysis"))

    assert f"{predictive_number}_Parameters.txt" in files_in_analysis
    assert f"{predictive_number}.bam" in files_in_analysis
    assert f"{predictive_number}.bam.bai" in files_in_analysis
    assert f"{predictive_number}_S6_L001_R1_001_converted.fasta" in files_in_analysis
    assert f"{predictive_number}_S6_L001_R2_001_converted.fasta" in files_in_analysis
    assert f"{predictive_number}_StatInfo.txt" in files_in_analysis
    assert "Reports" in files_in_analysis


@pytest.mark.parametrize("id_part", ["1", "5", "9"])
def test_correct_report_files(id_part):
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    expected_run_folder = os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000")

    predictive_number = f"mmci_predictive_00000000-0000-0000-0000-00000000000{id_part}"

    files_in_reports = os.listdir(os.path.join(expected_run_folder, "Samples",
                                               predictive_number, "Analysis", "Reports"))

    assert f"Settings" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1_Filtred_settings.txt" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1_Filtred.vcf" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1_settings.txt" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1_Statistics.txt" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1.txt" in files_in_reports
    assert f"{predictive_number}_Mutation_Report1.vcf" in files_in_reports


@pytest.mark.parametrize("id_part", ["1", "5", "9"])
def test_organise_without_analysis(id_part, remove_analysis_from_pseudonymized_file):
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    expected_run_folder = os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000")

    predictive_number = f"mmci_predictive_00000000-0000-0000-0000-00000000000{id_part}"

    assert os.path.exists(os.path.join(expected_run_folder, "Samples", predictive_number, "FASTQ"))

    assert not os.path.exists(os.path.join(expected_run_folder, "Samples", predictive_number, "Analysis"))


def test_important_run_metadata_files():
    organiser = RunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "2020_M00000_0000_00000000-00000",
                             FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    expected_run_folder = os.path.join(FAKE_DESTINATION_FILES, "2020", "MiSEQ", "00000",
                                       "2020_M00000_0000_00000000-00000")

    assert os.path.exists(os.path.join(expected_run_folder, "runParameters.xml"))
    assert os.path.exists(os.path.join(expected_run_folder, "GenerateFASTQRunStatistics.xml"))
    assert os.path.exists(os.path.join(expected_run_folder, "RunInfo.xml"))
    assert os.path.exists(os.path.join(expected_run_folder, "AnalysisLog.txt"))
