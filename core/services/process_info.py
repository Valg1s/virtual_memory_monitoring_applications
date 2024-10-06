import os
import sys
from pathlib import Path

import psutil
import GPUtil

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class ProcessInfoService(ServicesBase):
    service_name = "process_info_service"

    def __init__(self):
        super().__init__()

    @ServicesBase.exception
    def _classify_process(self, p):
        try:
            if p.open_files():
                return "current_processes"
            elif p.name() in ["System Idle Process", "System"]:
                return "system_processes"
            else:
                return "background_processes"
        except Exception as e:
            return "dont_have_access"

    def get_process_data(self):
        process_dict = {
            "current_processes": [],
            "system_processes": [],
            "background_processes": [],
            "dont_have_access": []
        }

        for process in psutil.process_iter(
                ['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'io_counters']):
            try:
                p_info = process.info
                process_type = self._classify_process(process)

                process_data = {
                    "process_id": p_info['pid'],
                    "process_name": p_info['name'],
                    "cpu_usage": process.cpu_percent(interval=0.1),
                    "ram_usage": self._convert_size(p_info['memory_info'].rss),  # в MB
                    "virtual_memory_usage": self._convert_size(p_info['memory_info'].vms),
                    "disk_usage": self._convert_size(process.io_counters().read_bytes + process.io_counters().write_bytes),
                }

                net_usage = sum([conn.raddr.port for conn in process.net_connections() if conn.raddr])
                process_data["network_usage"] = net_usage

                process_dict[process_type].append(process_data)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return process_dict
