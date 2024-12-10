import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.managers.monitoring_manager import MonitoringManager
except ImportError:
    exit("Cannot import monitoring_manager to ui")

manager = MonitoringManager()

