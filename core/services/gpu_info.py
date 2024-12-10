import sys
from pathlib import Path

import GPUtil

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class GPUInfoService(ServicesBase):
    service_name = "gpu_info_service"

    def __init__(self):
        super().__init__()

    @ServicesBase.exception
    def get_gpu_data(self):
        gpu_data = []

        gpus = GPUtil.getGPUs()

        if not gpus:
            gpu_data.append({
                "GPU": "GPU didn't find"
            })
        else:
            for i, gpu in enumerate(gpus):
                gpu_data.append({
                    "GPU": i + 1,
                    "Gpu Id": gpu.id,
                    "Gpu Name": gpu.name,
                    "Gpu Driver Version": gpu.driver,
                    "Gpu Memory": self._convert_size(gpu.memoryTotal * 1024 * 1024),
                    "Gpu Memory Used": self._convert_size(gpu.memoryUsed * 1024 * 1024),
                    "Gpu Memory Free": self._convert_size(gpu.memoryFree * 1024 * 1024),
                    "Gpu Load": f"{gpu.load * 100}%",
                    "Gpu Temperature": gpu.temperature,
                })

        return gpu_data
