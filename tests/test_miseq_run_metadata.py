from organiser.metadata_managers.miseq_run_metadata import CollectRunMetadata, RunInfoMMCI
import pytest
import shutil
import os
import json

FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_pseudonymized_runs" ,"2020_M00000_0000_00000000-00000")
FAKE_RUN_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_PSEUDONYMIZED_RUNS" ,"2020_M00000_0000_00000000-00000")


def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)

def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_RUN_FOR_TESTING)

@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    request.addfinalizer(_remove_coppied_fake_run)


def test_run_metadata_created_after_collection():
    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)

    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))

    response = collector()

    assert os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))
    assert response == True


def test_run_metadata_not_create_if_analysis_logs_file_missing():
    os.remove(os.path.join(FAKE_RUN_FOR_TESTING, "AnalysisLog.txt"))

    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)
    response = collector()

    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))

def test_run_metadata_not_create_if_run_parameters_file_missing():
    os.remove(os.path.join(FAKE_RUN_FOR_TESTING, "runParameters.xml"))

    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)
    response = collector()

    assert response == False
    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))


def test_run_metadata_not_create_if_generate_FASTQ_run_stat_file_missing():
    os.remove(os.path.join(FAKE_RUN_FOR_TESTING, "GenerateFASTQRunStatistics.xml"))

    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)
    response = collector()

    assert response == False
    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))


def test_run_metadata_not_create_if_run_info_file_missing():
    os.remove(os.path.join(FAKE_RUN_FOR_TESTING, "RunInfo.xml"))

    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)
    response = collector()

    assert response == False
    assert not os.path.exists(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json"))



def test_run_metadata_file_have_correct_data():
    collector = CollectRunMetadata(FAKE_RUN_FOR_TESTING)
    collector()

    with open(os.path.join(FAKE_RUN_FOR_TESTING, "run_metadata.json")) as f:
        data = json.load(f)

    assert data["idMMCI"] == "mis_001"
    assert data["seqDate"] == "2020-01-01"
    assert data["seqPlatform"] == "Illumina platform"
    assert data["seqMethod"] == "Illumina Sequencing"
    assert data["seqModel"] == "MiSeq"
    assert data["percentageQ30"] == "00.0%"
    assert data["percentageTR20"] == "NA"
    assert data["clusterPF"] == "00000000"
    assert data["numLanes"] == 0
    assert data["flowcellID"] == "000000000-00000"