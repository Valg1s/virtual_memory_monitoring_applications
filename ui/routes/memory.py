import sys
from pathlib import Path

from flask import jsonify

sys.path.append(str(Path(__file__).parent))

try:
    from base_rout import BaseView
except ImportError:
    exit("PC info rout:: Cannot import BaseView")

class MemoryView(BaseView):
    def get_memory_load(self):
        memory_load = self.manager.get_memory_load()

        return jsonify(memory_load)

    def get_virtual_memory_by_process(self):
        memory_load = self.manager.get_virtual_memory_of_processes()
        return jsonify(memory_load)