import sys
from pathlib import Path

from flask import jsonify

sys.path.append(str(Path(__file__).parent))

try:
    from base_rout import BaseView
except ImportError:
    exit("PC info rout:: Cannot import BaseView")

class PcInfoView(BaseView):
    def get_cpu_info(self):
        cpu_info = self.manager.get_cpu_info()
        return jsonify(cpu_info)

    def get_ram_info(self):
        ram_info = self.manager.get_ram_info()

        return jsonify(ram_info)

    def get_gpu_info(self):
        gpu_info = self.manager.get_gpu_info()
        return jsonify(gpu_info)

    def get_drives_info(self):
        drive_info = self.manager.get_drives_info()
        return jsonify(drive_info)

    def get_network_info(self):
        network_info = self.manager.get_network_info()
        return jsonify(network_info)

