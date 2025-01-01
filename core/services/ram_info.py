import re
import sys
from pathlib import Path
import subprocess
from functools import wraps
from itertools import groupby
from multiprocessing.dummy import Pool as ThreadPool

import psutil

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class RAMInfoService(ServicesBase):
    service_name = "ram_info_service"

    def __init__(self):
        super().__init__()

    def __map_form_factor(self, form_factor):
        form_factor_mapping = {
            0: 'Unknown',
            1: 'Other',
            2: 'SIP',
            3: 'DIP',
            4: 'ZIP',
            5: 'SOJ',
            6: 'Proprietary',
            7: 'SIMM',
            8: 'DIMM',
            9: 'TSOP',
            10: 'PGA',
            11: 'RIMM',
            12: 'SODIMM',
            13: 'SRIMM',
            14: 'SMD',
            15: 'SSMP',
            16: 'QFP',
            17: 'TQFP',
            18: 'SOIC',
            19: 'LCC',
            20: 'PLCC',
            21: 'BGA',
            22: 'FPBGA',
            23: 'LGA'
        }
        return form_factor_mapping.get(form_factor, "Unknown")

    def formate_ram_data(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)

            data = []
            for idx, ram in enumerate(result):
                data.append({
                    "ram_stick": idx + 1,
                    "ram_manufacturer": ram.get('Manufacturer', 'Unknown'),
                    "ram_capacity": f"{ram.get('Capacity', 'Unknown')} GB",
                    "ram_type": self.__map_memory_type(ram.get('MemoryType', ram.get('Type', 'Unknown'))),
                    "ram_speed": f"{ram.get('Speed', 'Unknown')} MHz",
                    "ram_data_width": f"{ram.get('DataWidth', 'Unknown')} bits",
                    "ram_part_number": ram.get('PartNumber', 'Unknown').strip(),
                    "ram_form_factor": ram.get('FormFactor', 'Unknown'),
                    "ram_serial_number": ram.get('SerialNumber', 'Unknown'),
                    "ram_voltage": ram.get('Voltage', 'Unknown'),
                    "ram_rank": ram.get('Rank', 'Unknown'),
                    "ram_configured_clock_speed": f"{ram.get('ConfiguredClockSpeed', 'Unknown')} MHz"
                })

                if type(data[idx]["ram_form_factor"]) == int:
                    data[idx]["ram_form_factor"] = self.__map_form_factor(data[idx]["ram_form_factor"])

            return data
        return wrapper

    def __parse_windows_ram(self, raw_data):
        """ Parse stripped PowerShell output into structured RAM details. """
        # Filter out empty lines
        filtered_data = [line.strip() for line in raw_data if line.strip()]

        # Group lines into chunks (one group per RAM module)
        groups = [list(group) for is_empty, group in groupby(filtered_data, key=lambda x: x.startswith("__")) if
                  not is_empty]

        ram_info = []

        for group in groups:
            ram_details = {}
            for line in group:
                # Match 'Key : Value' format
                match = re.match(r"^\s*(\w+)\s*:\s*(.*)$", line)
                if match:
                    key, value = match.groups()
                    ram_details[key.strip()] = value.strip()
            if ram_details:  # Add the module's details if it's not empty
                ram_info.append(ram_details)

        return ram_info

    # Example usage
    def __get_windows_ram_info(self):
        """
        Retrieves RAM information on Windows and structures it similar to Linux output.
        """
        ram_info = []
        try:
            # Fetch raw PowerShell output
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject -Class Win32_PhysicalMemory | Format-List"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True
            )

            stripped_output = result.stdout.splitlines()
            raw_data = self.__parse_windows_ram(stripped_output)

            # Structure the data to match the Linux format
            for ram in raw_data:
                stick_info = {
                    "Capacity": int(ram.get("Capacity", 0)) // (1024 ** 3),  # Bytes to GB
                    "Speed": ram.get("Speed", "").strip().replace(" MHz", ""),
                    "Configured Clock Speed": ram.get("ConfiguredClockSpeed", "").strip().replace(" MHz", ""),
                    "Manufacturer": ram.get("Manufacturer", "Unknown"),
                    "Type": ram.get("MemoryType", "Unknown"),
                    "Form Factor": int(ram.get("FormFactor", 0)),
                    "Part Number": ram.get("PartNumber", "").strip(),
                    "Serial Number": ram.get("SerialNumber", "").strip(),
                    "Rank": ram.get("InterleavePosition", "Unknown"),
                    "Voltage": ram.get("ConfiguredVoltage", "Unknown"),
                    "Data Width": ram.get("DataWidth", "").strip(),
                }
                ram_info.append(stick_info)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error retrieving RAM info: {e}")
            return []

        return ram_info

    @formate_ram_data
    def __get_linux_ram_info(self):
        ram_info = []
        result = subprocess.run(['sudo', 'dmidecode', '--type', 'memory'], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        stick_info = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Size:"):
                size_str = line.split(':')[1].strip()
                if "GB" in size_str:
                    stick_info['Capacity'] = int(float(size_str.split()[0]))  # Convert GB to integer
                elif "MB" in size_str:
                    stick_info['Capacity'] = int(float(size_str.split()[0]) / 1024)  # Convert MB to GB
            elif line.startswith("Speed:"):
                stick_info['Speed'] = line.split(':')[1].strip().replace(" MHz", "")
            elif line.startswith("Configured Clock Speed:"):
                stick_info['ConfiguredClockSpeed'] = line.split(':')[1].strip().replace(" MHz", "")
            elif line.startswith("Manufacturer:"):
                stick_info['Manufacturer'] = line.split(':')[1].strip()
            elif line.startswith("Type:"):
                stick_info['Type'] = line.split(':')[1].strip()
            elif line.startswith("Form Factor:"):
                stick_info['FormFactor'] = line.split(':')[1].strip()
            elif line.startswith("Part Number:"):
                stick_info['PartNumber'] = line.split(':')[1].strip()
            elif line.startswith("Serial Number:"):
                stick_info['SerialNumber'] = line.split(':')[1].strip()
            elif line.startswith("Rank:"):
                stick_info['Rank'] = line.split(':')[1].strip()
            elif line.startswith("Voltage:"):
                stick_info['Voltage'] = line.split(':')[1].strip()
            elif line.startswith("Data Width:"):
                stick_info['DataWidth'] = line.split(':')[1].strip().replace(" bits", "")

            if line == '' and stick_info:  # End of each stick info
                ram_info.append(stick_info)
                stick_info = {}

        return ram_info

    def __map_memory_type(self, memory_type):
        memory_type_mapping = {
            20: 'DDR',
            21: 'DDR2',
            24: 'DDR3',
            26: 'DDR4',
            'DDR': 'DDR',
            'DDR2': 'DDR2',
            'DDR3': 'DDR3',
            'DDR4': 'DDR4',
            'Unknown': 'Unknown'
        }
        return memory_type_mapping.get(memory_type, "Unknown")

    @ServicesBase.exception
    def get_memory_data(self):
        result = "Unknown"

        if psutil.WINDOWS:
            result = self.__get_windows_ram_info()
        if psutil.LINUX:
            result = self.__get_linux_ram_info()

        return result

    def get_ram_usage(self):
        max_ram_memory = psutil.virtual_memory().total

        current_ram_usage = psutil.virtual_memory().used

        max_virtual_memory = psutil.swap_memory().total

        current_virtual_memory_usage = psutil.swap_memory().used

        return {
            "max_ram_memory": max_ram_memory,
            "current_ram_usage": current_ram_usage,
            "max_virtual_memory": max_virtual_memory,
            "current_virtual_memory_usage": current_virtual_memory_usage
        }

    def _get_virtual_memory_by_pid(self, pid):
        try:
            proc = psutil.Process(pid)
            proc_virtual_memory = self._convert_size(proc.memory_info().vms)
            return {
                "PID": pid,
                "Process Name": proc.name(),
                "Virtual Memory Usage": proc_virtual_memory,
            }
        except psutil.NoSuchProcess:
            return {"PID": pid,"Process Name":"None", "Virtual Memory Usage": "No process found"}
        except Exception as e:
            return {"PID": pid,"Process Name":"None","Virtual Memory Usage": f"Error: {e}"}

    def get_virtual_memory_of_processes(self):
        tasks = [proc.info["pid"] for proc in psutil.process_iter(["pid"])]

        with ThreadPool(processes=24) as pool:
            result = pool.map(self._get_virtual_memory_by_pid, tasks)

        return result