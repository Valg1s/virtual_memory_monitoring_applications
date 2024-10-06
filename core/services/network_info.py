import sys
import socket
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
        network_data = []

        public_ip = self.get_public_ip()
        isp_info = self.get_internet_provider(public_ip)

        interfaces = psutil.net_if_addrs()
        interface_stats = psutil.net_if_stats()
        net_io = psutil.net_io_counters(pernic=True)

        for interface_name, addresses in interfaces.items():
            stats = interface_stats.get(interface_name, None)
            io_counters = net_io.get(interface_name, None)

            data = {
                "interface": interface_name,
                "status": "up" if stats and stats.isup else "down",
                "addresses": [],
                "isp": isp_info,
                "public_ip": public_ip,
                "usage": {
                    "bytes_sent": io_counters.bytes_sent if io_counters else 0,
                    "bytes_received": io_counters.bytes_recv if io_counters else 0
                }
            }

            for addr in addresses:
                data["addresses"].append({
                    "family": addr.family.name,
                    "address": addr.address,
                    "netmask": addr.netmask if addr.netmask else "N/A",
                    "broadcast": addr.broadcast if addr.broadcast else "N/A"
                })

            network_data.append(data)

        return network_data
