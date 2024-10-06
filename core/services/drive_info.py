import sys
from pathlib import Path

import psutil

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class DriveInfoService(ServicesBase):
    service_name = "drive_info_service"

    def __init__(self):
        super().__init__()

    @ServicesBase.exception
    def get_drive_data(self):
        drive_data = []
        partitions = psutil.disk_partitions()

        for partition in partitions:
            partition_usage = psutil.disk_usage(partition.mountpoint)

            drive_info = {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": self._convert_size(partition_usage.total),
                "used": self._convert_size(partition_usage.used),
                "free": self._convert_size(partition_usage.free),
                "percent": f"{partition_usage.percent} %",
            }
            drive_data.append(drive_info)

        return drive_data
