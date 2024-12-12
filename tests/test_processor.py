import pytest
import os
import shutil
from organiser.process.processor import Processor

FAKE_ALL_RUNS_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS")
FAKE_ALL_RUNS_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs")

FAKE_DESTINATION_FILES = os.path.join(os.path.dirname(__file__), "test_destination")
FAKE_PATIENT_FILES = os.path.join(os.path.dirname(__file__), "test_patients")

FAKE_OLD_MISEQ_PATH = os.path.join(FAKE_ALL_RUNS_FOR_COPY, "200101_M00000_0000_00000000-00000")
FAKE_NEW_MISEQ_PATH = os.path.join(FAKE_ALL_RUNS_FOR_COPY, "240101_M00000_0000_00000000-00000")
FAKE_NEXTSEQ_PATH = os.path.join(FAKE_ALL_RUNS_FOR_COPY, "230101_N0000000_0000_0000000000")

FAKE_OLD_MISEQ_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "200101_M00000_0000_00000000-00000")
FAKE_NEW_MISEQ_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "240101_M00000_0000_00000000-00000")

FAKE_NEXTSEQ_FOR_TESTING = os.path.join(FAKE_ALL_RUNS_FOR_TESTING, "230101_N0000000_0000_0000000000")


def _copy_fake_folders():
    os.mkdir(FAKE_PATIENT_FILES)
    os.mkdir(FAKE_DESTINATION_FILES)


def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_ALL_RUNS_FOR_TESTING)
    shutil.rmtree(FAKE_PATIENT_FILES)
    shutil.rmtree(FAKE_DESTINATION_FILES)


@pytest.fixture(autouse=True)
def setup_and_teardown_test_files(request):
    _copy_fake_folders()
    request.addfinalizer(_remove_coppied_fake_run)


@pytest.fixture
def setup_and_teardown_old_miseq():
    shutil.copytree(FAKE_OLD_MISEQ_PATH, FAKE_OLD_MISEQ_FOR_TESTING)


@pytest.fixture
def setup_and_teardown_new_miseq():
    shutil.copytree(FAKE_NEW_MISEQ_PATH, FAKE_NEW_MISEQ_FOR_TESTING)


@pytest.fixture
def setup_and_teardown_nextseq():
    shutil.copytree(FAKE_NEXTSEQ_PATH, FAKE_NEXTSEQ_FOR_TESTING)

@pytest.fixture
def mocked_old_miseq_organise_run(mocker):
    return mocker.patch("organiser.run_organisers.old_miseq_organise_run.OldMiseqRunOrganiser.organise_run")


@pytest.fixture
def mocked_new_miseq_organise_run(mocker):
    return mocker.patch("organiser.run_organisers.new_miseq_organise_run.NewMiseqRunOrganiser.organise_run")


@pytest.fixture
def mocked_nextseq_organise_run(mocker):
    return mocker.patch("organiser.run_organisers.nextseq_organise_run.NextSeqRunOrganiser.organise_run")


def test_select_old_miseq(setup_and_teardown_old_miseq, mocked_old_miseq_organise_run, mocked_new_miseq_organise_run,
                          mocked_nextseq_organise_run):
    processor = Processor(FAKE_ALL_RUNS_FOR_TESTING,
                          FAKE_DESTINATION_FILES,
                          FAKE_PATIENT_FILES)
    processor.process_runs()
    mocked_old_miseq_organise_run.assert_called_once()
    mocked_new_miseq_organise_run.assert_not_called()
    mocked_nextseq_organise_run.assert_not_called()


def test_select_new_miseq(setup_and_teardown_new_miseq, mocked_new_miseq_organise_run, mocked_old_miseq_organise_run,
                          mocked_nextseq_organise_run):
    processor = Processor(FAKE_ALL_RUNS_FOR_TESTING,
                          FAKE_DESTINATION_FILES,
                          FAKE_PATIENT_FILES)
    processor.process_runs()
    mocked_new_miseq_organise_run.assert_called_once()
    mocked_old_miseq_organise_run.assert_not_called()
    mocked_nextseq_organise_run.assert_not_called()


def test_new_and_old_miseq_called(setup_and_teardown_new_miseq, setup_and_teardown_old_miseq,
                                  mocked_new_miseq_organise_run, mocked_old_miseq_organise_run,
                                  mocked_nextseq_organise_run):
    processor = Processor(FAKE_ALL_RUNS_FOR_TESTING,
                          FAKE_DESTINATION_FILES,
                          FAKE_PATIENT_FILES)
    processor.process_runs()
    mocked_new_miseq_organise_run.assert_called_once()
    mocked_old_miseq_organise_run.assert_called_once()
    mocked_nextseq_organise_run.assert_not_called()


def test_select_nextseq(setup_and_teardown_nextseq,
                        mocked_nextseq_organise_run,
                        mocked_old_miseq_organise_run,
                        mocked_new_miseq_organise_run):

    processor = Processor(FAKE_ALL_RUNS_FOR_TESTING,
                          FAKE_DESTINATION_FILES,
                          FAKE_PATIENT_FILES)
    processor.process_runs()

    mocked_nextseq_organise_run.assert_called_once()
    mocked_old_miseq_organise_run.assert_not_called()
    mocked_new_miseq_organise_run.assert_not_called()

