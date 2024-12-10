import sys
from pathlib import Path

import psutil
import requests

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from core.base.services_base import ServicesBase
except ImportError as e:
    exit(f"Cannot import logger module: {e}")


class NetworkInfoService(ServicesBase):
    service_name = "network_info_service"

    def __init__(self):
        super().__init__()

    def get_public_ip(self):
        try:
            response = requests.get("https://api.ipify.org?format=json")
            return response.json().get("ip", "Unknown IP")
        except requests.RequestException:
            return "Unable to get public IP"

    def get_internet_provider(self,ip_address):
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json")
            data = response.json()
            return data.get("org", "Unknown ISP")  # Organization name (ISP)
        except requests.RequestException:
            return "Unable to get ISP information"

    @ServicesBase.exception
    def get_network_data(self):
        public_ip = self.get_public_ip()
        isp_info = self.get_internet_provider(public_ip)

        net_io = psutil.net_io_counters(pernic=True)
        total_bytes_sent = sum(interface.bytes_sent for interface in net_io.values())
        total_bytes_received = sum(interface.bytes_recv for interface in net_io.values())

        data = {
            "ISP(Provider)": isp_info,
            "Public Ip": public_ip,
            "Bytes Sends": self._convert_size(total_bytes_sent),
            "Bytes Received": self._convert_size(total_bytes_received)
        }

        return data
