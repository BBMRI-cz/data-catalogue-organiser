import pytest
import os
import shutil

from organiser.run_organisers.nextseq_organise_run import NextSeqRunOrganiser

FAKE_ALL_RUNS_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS")
FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs",
                                 "230101_N0000000_0000_0000000000")

FAKE_RUN_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000")
FAKE_DESTINATION_FILES = os.path.join(os.path.dirname(__file__), "test_destination")
FAKE_PATIENT_FILES = os.path.join(os.path.dirname(__file__), "test_patients")

def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)
    os.mkdir(FAKE_DESTINATION_FILES)
    os.mkdir(FAKE_PATIENT_FILES)

def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_ALL_RUNS_FOR_TESTING)
    shutil.rmtree(FAKE_PATIENT_FILES)
    shutil.rmtree(FAKE_DESTINATION_FILES)

@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    request.addfinalizer(_remove_coppied_fake_run)


@pytest.fixture
def remove_fastq_folders():
    shutil.rmtree(os.path.join(FAKE_RUN_FOR_TESTING, "FASTQ"))


def test_run_is_in_correct_sturecture():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000"))

def test_data_folder_structred():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                       "Data", "Intensities", "BaseCalls"))
    for i in range(1,5):
        assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                           "Data", "Intensities", f"L00{i}"))

def test_samples_folder_contains_fastq_files():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                       "Samples"))

def test_individual_fastq_files():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    for i in range(8):
        sample_files = os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                           "Samples")
        assert os.path.exists(os.path.join(sample_files, f"2023_000{i}_DNA", "FASTQ"))
        assert os.path.exists(os.path.join(sample_files, f"2023_000{i}_RNA", "FASTQ"))
        assert all([file.endswith("fastq.gz") for file in os.listdir(os.path.join(sample_files,
                                                                                  f"2023_000{i}_DNA",
                                                                                  "FASTQ"))])
        assert len(os.listdir(os.path.join(sample_files, f"2023_000{i}_DNA", "FASTQ"))) == 8

def test_missing_fastq_files(remove_fastq_folders):
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()
    sample_files = os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                "Samples")
    assert not os.path.exists(os.path.join(sample_files, "2023_0000_DNA", "FASTQ"))
    for i in range(8):
        assert os.path.exists(os.path.join(sample_files, f"2023_000{i}_DNA"))
        assert os.path.exists(os.path.join(sample_files, f"2023_000{i}_RNA"))


@pytest.mark.parametrize("filename", ["SampleSheet.csv", "RunParameters.xml", "RunInfo.xml", "RunCompletionStatus.xml"])
def test_individual_nextseq_files(filename):
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq", "230101_N0000000_0000_0000000000",
                                       filename))


def test_catalogue_info_pred_number():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq",
                                       "230101_N0000000_0000_0000000000", "catalog_info_per_pred_number"))

def test_catalog_info_missing_no_error(remove_catalog_info_per_pred_number):
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()

    assert not os.path.exists(os.path.join(FAKE_DESTINATION_FILES, "2023", "NextSeq",
                                       "230101_N0000000_0000_0000000000", "catalog_info_per_pred_number"))


def test_patient_correctly_created_in_tree():
    organiser = NextSeqRunOrganiser(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000",
                                    FAKE_DESTINATION_FILES, FAKE_PATIENT_FILES)
    organiser.organise_run()


    assert os.path.exists(os.path.join(FAKE_PATIENT_FILES, "2000", "mmci_patient_00000000-0000-0000-0000-000000000001",
                                       "patient_metadata.json"))


@pytest.fixture
def remove_catalog_info_per_pred_number():
    shutil.rmtree(os.path.join(FAKE_RUN_FOR_TESTING, "catalog_info_per_pred_number"))
