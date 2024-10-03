import pytest
import os
import shutil

from organiser.run_organisers.new_miseq_organise_run import NewMiseqOrganiseRun

FAKE_ALL_RUNS_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS")
FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs",
                                 "240101_M00000_0000_00000000-00000")


FAKE_RUN_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "240101_M00000_0000_00000000-00000")
FAKE_DESTINATION_FILES = os.path.join(os.path.dirname(__file__), "test_destination")
FAKE_PATIENT_FILES = os.path.join(os.path.dirname(__file__), "test_patients")


EXPECTED_ORGANISED_FILE_PATH = os.path.join(FAKE_DESTINATION_FILES,
                                            "2024",
                                            "MiSEQ",
                                            "240101_M00000_0000_00000000-00000")


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


def get_organiser():
    return NewMiseqOrganiseRun(FAKE_ALL_RUNS_FOR_TESTING, "240101_M00000_0000_00000000-00000",
                               FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)


def test_folder_structure_correct():
    organiser = get_organiser()
    organiser.organise_run()

    assert os.path.exists(EXPECTED_ORGANISED_FILE_PATH)


def test_alignment_correct():
    organiser = get_organiser()
    organiser.organise_run()

    assert os.path.exists(os.path.join(EXPECTED_ORGANISED_FILE_PATH, "Alignment"))


def test_catalog_info_per_pred_number():
    organiser = get_organiser()
    organiser.organise_run()

    assert os.path.exists(os.path.join(EXPECTED_ORGANISED_FILE_PATH, "catalog_info_per_pred_number"))


def test_catalog_info_missing_no_error(remove_catalog_info_per_pred_number):
    organiser = get_organiser()
    organiser.organise_run()

    assert not os.path.exists(os.path.join(EXPECTED_ORGANISED_FILE_PATH, "catalog_info_per_pred_number"))


def test_important_files_coppied():
    important_files = ["AnalysisLog.txt", "CompletedJobInfo.xml", "RunParameters.xml",
                       "RunInfo.xml", "SampleSheet.csv", "GenerateFASTQRunStatistics.xml"]
    organiser = get_organiser()
    organiser.organise_run()
    for file in important_files:
        assert os.path.exists(os.path.join(EXPECTED_ORGANISED_FILE_PATH, file))


def test_fastq_files_coppied():
    organiser = get_organiser()
    organiser.organise_run()
    for i in range(1, 20):
        assert os.path.exists(os.path.join(EXPECTED_ORGANISED_FILE_PATH,
                                           "Samples",
                                           f"mmci_predictive_00000000-0000-0000-0000-0000000000{str(i).zfill(2)}",
                                           "FASTQ"))


def test_analysis_files():
    organiser = get_organiser()
    organiser.organise_run()

    for i in range(1, 20):
        predictive_path = f"mmci_predictive_00000000-0000-0000-0000-0000000000{str(i).zfill(2)}"
        expected_path_to_analysis = os.path.join(EXPECTED_ORGANISED_FILE_PATH, "Samples", predictive_path, "Analysis")
        assert os.path.exists(expected_path_to_analysis)
        assert os.path.exists(os.path.join(expected_path_to_analysis, "Reports"))

        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}.bam"))
        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}.bam.bai"))

        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}_Parameters.txt"))
        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}_StatInfo.txt"))

        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}_S6_L001_R1_001_convert.log"))
        assert os.path.exists(os.path.join(expected_path_to_analysis,
                                           f"{predictive_path}_S6_L001_R1_001_converted.fasta"))
        assert os.path.exists(os.path.join(expected_path_to_analysis, f"{predictive_path}_S6_L001_R2_001_convert.log"))
        assert os.path.exists(os.path.join(expected_path_to_analysis,
                                           f"{predictive_path}_S6_L001_R2_001_converted.fasta"))


@pytest.fixture
def remove_catalog_info_per_pred_number():
    shutil.rmtree(os.path.join(FAKE_RUN_FOR_TESTING, "catalog_info_per_pred_number"))
