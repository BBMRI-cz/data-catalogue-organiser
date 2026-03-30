import pytest
from organiser.logging_config.logging_config import LoggingConfig

@pytest.fixture(autouse=True)
def init_logger_for_tests(tmp_path):
    LoggingConfig.initialize("FAKE_RUN_ID", tmp_path)
