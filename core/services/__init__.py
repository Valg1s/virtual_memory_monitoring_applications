from .cpu_info import CPUInfoService
from .drive_info import DriveInfoService
from .gpu_info import GPUInfoService
from .network_info import NetworkInfoService
from .ram_info import RAMInfoService
from .process_info import ProcessInfoService

cpu_service = CPUInfoService
ram_service = RAMInfoService
gpu_service = GPUInfoService
drives_service = DriveInfoService
network_service = NetworkInfoService
process_service = ProcessInfoService
