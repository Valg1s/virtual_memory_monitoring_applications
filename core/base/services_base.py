import os
import sys
from pathlib import Path
from functools import wraps

import math

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.logger.native_logger import init_logger
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class ServicesBase:
    service_name = "service_base"

    def __init__(self):
        self.project_dir = str(Path(__file__).parent.parent.parent)

        self.logger = init_logger(name=self.service_name, log_dir_path=os.path.join(self.project_dir, "logs"))

    def exception(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                result = method(self, *args,**kwargs)

                if not result:
                    self.logger.info("Task do not return data")
                    return False

                return result
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return Exception

        return wrapper

    @exception
    def _convert_size(self, size_bytes):
        if size_bytes == 'N/A':
            return size_bytes
        size_bytes = int(size_bytes)
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"