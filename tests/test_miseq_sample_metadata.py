from organiser.metadata_managers.miseq_sample_metadata import CollectSampleMetadata
import pytest
import shutil
import os
import json


FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs" ,"2020_M00000_0000_00000000-00000")
FAKE_RUN_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS" ,"2020_M00000_0000_00000000-00000")

FAKE_SAMPLE_DATA = os.path.join(FAKE_RUN_FOR_TESTING, "Analysis", "mmci_predictive_00000000-0000-0000-0000-000000000001_Output", "mmci_predictive_00000000-0000-0000-0000-000000000001", "mmci_predictive_00000000-0000-0000-0000-000000000001_StatInfo.txt")
FAKE_CATALOGUE_INFO = os.path.join(FAKE_RUN_FOR_TESTING, "catalog_info_per_pred_number")

def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)

def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_RUN_FOR_TESTING)

@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    request.addfinalizer(_remove_coppied_fake_run)


def test_files_created():
    CollectSampleMetadata(FAKE_RUN_FOR_TESTING, FAKE_SAMPLE_DATA, FAKE_CATALOGUE_INFO)()

    assert os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "sample_metadata", "mmci_predictive_00000000-0000-0000-0000-000000000001.json"))


def test_extracted_correct_metadata():
    CollectSampleMetadata(FAKE_RUN_FOR_TESTING, FAKE_SAMPLE_DATA, FAKE_CATALOGUE_INFO)()

    with open(os.path.join(FAKE_RUN_FOR_TESTING, "sample_metadata", "mmci_predictive_00000000-0000-0000-0000-000000000001.json")) as f:
        data = json.load(f)

    assert data["idSample"] == "mmci_predictive_00000000-0000-0000-0000-000000000001"
    assert data["collFromPerson"] == "mmci_patient_00000000-0000-0000-0000-000000000001"
    assert data["belToDiag"] == "mmci_clinical_00000000-0000-0000-0000-000000000001"
    assert data["bioSpeciType"] == "Frozen Tissue"
    assert data["pathoState"] == "Tumor"
    assert data["storCond"] == "Cryotube 1–2mL Programmable freezing to <-135°C"
    assert data["wsiAvailability"] == False
    assert data["radioDataAvailability"] == False
    assert data["avReadDepth"] == "2400,00"
    assert data["obsReadLength"] == "130"