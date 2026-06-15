import time

from adapter.sim.sim_adapter import SimAdapter
from mapping.mcdu_mapping import McduMapping
from connector.xplane.xplane_connect import XPlaneConnectX

class XPlaneAdapter(SimAdapter):
    def __init__(self, xplane_ip: str, xplane_port: int, mcdu_mapping: McduMapping):
        if None is xplane_ip:
            raise ValueError("xplane_ip cannot be None")
        if None is xplane_port:
            raise ValueError("xplane_port cannot be None")
        if None is mcdu_mapping:
            raise ValueError("mcdu_mapping cannot be None")

        self.mcdu_mapping = mcdu_mapping
        self.xpc = XPlaneConnectX(ip=xplane_ip, port=xplane_port)

    def close(self):
        self.xpc.close()

    def send_command(self, command):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] key: {repr(command)}")

        cmd = self.mcdu_mapping.get(command)
        if cmd:
            self.xpc.sendCMND(cmd)
            print(f"[XPLANE] Sent: {command} -> {cmd}")
        else:
            print(f"[XPLANE] No such command for: {command}")
