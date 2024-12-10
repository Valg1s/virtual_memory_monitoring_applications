import sys
from pathlib import Path
from datetime import datetime, timedelta

import psutil
import cpuinfo

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class CPUInfoService(ServicesBase):
    service_name = "cpu_info_service"

    def __init__(self):
        super().__init__()

    @ServicesBase.exception
    def get_cpu_data(self):
        cpu = cpuinfo.get_cpu_info()

        cpu_info = {
            "Manufacturer": cpu.get('vendor_id_raw', 'N/A'),
            "Processor Model": cpu.get('brand_raw', 'N/A'),
            "Architecture": cpu.get('arch', 'N/A'),
            "Number of Physical Cores": psutil.cpu_count(logical=False),
            "Number of Logical Threads": psutil.cpu_count(logical=True),
            "L1 Cache (KB)": self._convert_size(cpu.get('l1_data_cache_size', 'N/A')),
            "L2 Cache (KB)": self._convert_size(cpu.get('l2_cache_size', 'N/A')),
            "L3 Cache (KB)": self._convert_size(cpu.get('l3_cache_size', 'N/A')),
        }

        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info["CPU Frequency (GHz)"] = f"{round(cpu_freq.current / 1000, 2)} GHz"
            cpu_info["Minimum Frequency (GHz)"] = f"{round(cpu_freq.min / 1000, 2)} GHz"
            cpu_info["Maximum Frequency (GHz)"] = f"{round(cpu_freq.max / 1000, 2)} GHz"
        else:
            cpu_info["CPU Frequency (GHz)"] = f"N/A"
            cpu_info["Minimum Frequency (GHz)"] = 'N/A'
            cpu_info["Maximum Frequency (GHz)"] = 'N/A'

        return cpu_info

    def _format_cpu_usage_time(self, time):
        time_delta = timedelta(seconds=time)

        # Extract days, hours, minutes, and seconds
        total_days = time_delta.days
        total_seconds = time_delta.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Format the string as "days:hours:minutes:seconds"
        formatted_time = f"{total_days}:{hours:02}:{minutes:02}:{seconds:02}"

        return formatted_time

    def get_cpu_load(self):
        cpu_freq = psutil.cpu_freq(percpu=False).current
        cpu_load = psutil.cpu_percent(interval=3, percpu=True)
        work_time = psutil.cpu_times().user

        result_data = {
            "cpu_freq": cpu_freq,
            "cpu_load": max(cpu_load),
            "work_time": self._format_cpu_usage_time(work_time),
        }

        return result_data