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

        cpu_load = 0

        for process in psutil.process_iter(
                ['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'io_counters']):
            try:
                p_info = process.info
                process_type = self._classify_process(process)
                cur_cpu_load = process.cpu_percent(interval=0.01)
                cpu_load += cur_cpu_load

                process_data = {
                    "Process Id": p_info['pid'],
                    "Process Name": p_info['name'],
                    "Cpu Usage": cur_cpu_load,
                    "Ram Usage": self._convert_size(p_info['memory_info'].rss),  # в MB
                    "Virtual Memory Usage": self._convert_size(p_info['memory_info'].vms),
                    "Disk Usage": self._convert_size(process.io_counters().read_bytes + process.io_counters().write_bytes),
                }

                net_usage = sum([conn.raddr.port for conn in process.net_connections() if conn.raddr])
                process_data["network_usage"] = net_usage

                process_dict[process_type].append(process_data)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        print(cpu_load)
        return process_dict
