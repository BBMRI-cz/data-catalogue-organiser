import os
import logging
import sys

class LoggingConfig:
    _logger : logging.Logger | None = None
    _run_id : str | None = None
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    @classmethod
    def initialize(cls, run_id: str, log_dir: str) -> logging.Logger:
        cls._run_id = run_id
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f"{run_id}.log")

        logger = logging.getLogger(f"run.{run_id}")

        log_level_env = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level_env not in cls.LOG_LEVELS:
            raise ValueError(f"Invalid LOG_LEVEL '{log_level_env}'. Must be one of {list(cls.LOG_LEVELS.keys())}")

        log_level = cls.LOG_LEVELS[log_level_env]

        logger.setLevel(log_level)


        if not logger.handlers:  
            # file logging
            file_handler = logging.FileHandler(log_filename)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # stdout logging
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        cls._logger = logger

        logger.info(f"Logger initialized with level: {log_level_env}")

        return logger

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            raise RuntimeError("Logger not initialized. Call LoggingConfig.initialize(run_id) first.")
        return cls._logger
