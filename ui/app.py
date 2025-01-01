import os
from pathlib import Path

from flask import Flask, render_template

base_path = Path(__file__).parent

try:
    from routes.pc_info import PcInfoView
except ImportError:
    exit("APP:: Cannot import PCInfoView")

try:
    from routes.cpu import CPUView
except ImportError:
    exit("APP:: Cannot import CPUView")

try:
    from routes.memory import MemoryView
except ImportError:
    exit("APP:: Cannot import MemoryView")

try:
    from routes.gpu import GPUView
except ImportError:
    exit("APP:: Cannot import GPUView")

app = Flask(__name__,
            static_folder=os.path.join(base_path,'static/'),  # Path to your static files
            template_folder=os.path.join(base_path,'templates/')
            )# Path to your templates

@app.route('/')
def home():
    return render_template('main_page.html')

pc_info = PcInfoView()
cpu_info = CPUView()
memory_info = MemoryView()
gpu_info = GPUView()

app.add_url_rule('/get_cpu_info', endpoint='pc_cpu_info', view_func=pc_info.get_cpu_info)
app.add_url_rule('/get_ram_info', endpoint='pc_ram_info', view_func=pc_info.get_ram_info)
app.add_url_rule('/get_gpu_info', endpoint='pc_gpu_info', view_func=pc_info.get_gpu_info)
app.add_url_rule('/get_drives_info', endpoint='pc_drives_info', view_func=pc_info.get_drives_info)
app.add_url_rule('/get_network_info', endpoint='pc_network_info', view_func=pc_info.get_network_info)

app.add_url_rule('/get_cpu_load', endpoint='cpu_load', view_func=cpu_info.get_cpu_load)
app.add_url_rule('/get_memory_load', endpoint='memory_load', view_func=memory_info.get_memory_load)
app.add_url_rule('/get_gpu_load', endpoint='gpu_load', view_func=gpu_info.get_gpu_load)
app.add_url_rule('/get_virtual_memory', endpoint='virtual_memory', view_func=memory_info.get_virtual_memory_by_process)

if __name__ == "__main__":
    app.run(debug=True, port=8080)