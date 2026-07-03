#  Copyright (c) 2026
#  United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
#  All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
#  Source may not be released without written approval from HEC

import logging
import os


def _get_log_level():
    log_level_name = os.environ.get("REGI_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, None)
    invalid_log_level = not isinstance(log_level, int)
    if invalid_log_level:
        log_level = logging.INFO
    return log_level, invalid_log_level, log_level_name

def configure_logging():
    log_level, invalid_log_level, log_level_name = _get_log_level()

    log_format = os.environ.get(
        "REGI_LOG_FORMAT",
        "%(asctime)s %(levelname)s %(name)s "
        "[job=%(aws_batch_job_id)s attempt=%(aws_batch_job_attempt)s] - %(message)s",
    )

    class AwsBatchFilter(logging.Filter):
        def filter(self, record):
            record.aws_batch_job_id = os.environ.get("AWS_BATCH_JOB_ID", "-")
            record.aws_batch_job_attempt = os.environ.get("AWS_BATCH_JOB_ATTEMPT", "-")
            return True

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(AwsBatchFilter())

    logger = logging.getLogger("regi-launcher")
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    if invalid_log_level:
        logger.warning("Invalid REGI_LOG_LEVEL '%s'; using INFO.", log_level_name)

    return logger