import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.logger.native_logger import init_logger
except ImportError as e:
    exit(f"Cannot import logger module: {e}")

try:
    from core.services import *
except ImportError as e:
    exit(f"Cannot import services: {e}")


class MonitoringManager:
    service_name = "monitor_manager"

    def __init__(self):
        self.project_dir = str(Path(__file__).parent.parent.parent)

        self.logger = init_logger(name=self.service_name, log_dir_path=os.path.join(self.project_dir, "logs"))

        self.cpu = cpu_service()
        self.ram = ram_service()
        self.gpu = gpu_service()
        self.drives = drives_service()
        self.network = network_service()
        self.process = process_service()

    def get_cpu_info(self):
        return self.cpu.get_cpu_data()

    def get_ram_info(self):
        return self.ram.get_memory_data()

    def get_gpu_info(self):
        return self.gpu.get_gpu_data()

    def get_drives_info(self):
        return self.drives.get_drive_data()

    def get_network_info(self):
        return self.network.get_network_data()

    def get_process_info(self):
        return self.process.get_process_data()

    def test(self):
        print(self.get_cpu_info())
        print(self.get_ram_info())
        print(self.get_gpu_info())
        print(self.get_drives_info())
        print(self.get_network_info())
        print(self.get_process_info())


if __name__ == '__main__':
    t = MonitoringManager()
    t.test()
    