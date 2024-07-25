from organiser.metadata_managers.miseq_run_metadata import CollectRunMetadata, RunInfoMMCI
import pytest
import shutil
import os

FAKE_RUN_FOR_COPY = "test_run"
FAKE_RUN_FOR_TESTING = "FAKE_RUN"

def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)

def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_RUN_FOR_TESTING)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run(FAKE_RUN_FOR_TESTING)
    request.addfinalizer(_remove_coppied_fake_run)


def test_basic_functionality():
    collector = CollectRunMetadata("test_run")

    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))

    collector()

    assert os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))