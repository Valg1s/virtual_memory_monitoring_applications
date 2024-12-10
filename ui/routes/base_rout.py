import sys
from pathlib import Path

from flask.views import View

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from ui.config import manager
except ImportError as e:
    exit("Cannot import manager from init")


class BaseView(View):
    def __init__(self, **kwargs):
        self.manager = manager

        for key,item in kwargs.items():
            setattr(self, key, item)