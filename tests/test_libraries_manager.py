import pytest
import os
from organiser.manage_libraries import LibrariesManager

import shutil

FAKE_RUN_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_run")
FAKE_RUN_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_RUN")

FAKE_LIBRARIES_FOR_COPY = os.path.join(os.path.dirname(__file__), "test_libraries")
FAKE_LIBRARIES_FOR_TESTING = os.path.join(os.path.dirname(__file__), "FAKE_LIBRARIES")


def _copy_fake_run():
    shutil.copytree(FAKE_RUN_FOR_COPY, FAKE_RUN_FOR_TESTING)

def _copy_fake_libraries():
    shutil.copytree(FAKE_LIBRARIES_FOR_COPY, FAKE_LIBRARIES_FOR_TESTING)

def _remove_coppied_fake_run():
    shutil.rmtree(FAKE_RUN_FOR_TESTING)

def _remove_coppied_fake_libraries():
    shutil.rmtree(FAKE_LIBRARIES_FOR_TESTING)

@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    _copy_fake_libraries()
    request.addfinalizer(_remove_coppied_fake_run)
    request.addfinalizer(_remove_coppied_fake_libraries)


@pytest.fixture(autouse=True)
def setup_and_teardown_organise_files(request):
    _copy_fake_run()
    request.addfinalizer(_remove_coppied_fake_run)