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
                    "gpu_id": gpu.id,
                    "gpu_name": gpu.name,
                    "gpu_driver": gpu.driver,
                    "gpu_memory": self._convert_size(gpu.memoryTotal * 1024 * 1024),
                })

        return gpu_data
