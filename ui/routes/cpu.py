import sys
from pathlib import Path

from flask import jsonify

sys.path.append(str(Path(__file__).parent))

try:
    from base_rout import BaseView
except ImportError:
    exit("PC info rout:: Cannot import BaseView")

class CPUView(BaseView):
    def get_cpu_load(self):
        cpu_load = self.manager.get_cpu_load()

        return jsonify(cpu_load)