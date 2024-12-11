import sys
from pathlib import Path

from flask import jsonify

sys.path.append(str(Path(__file__).parent))

try:
    from base_rout import BaseView
except ImportError:
    exit("PC info rout:: Cannot import BaseView")

class GPUView(BaseView):
    def get_gpu_load(self):
        gpu_load = self.manager.get_gpu_load()

        return jsonify(gpu_load)