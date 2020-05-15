"""
Scan for specific beacons and provide and HTTP API to query RSSI.
"""

from bluepy.btle import Scanner
from datetime import datetime
import threading
from aiohttp import web

# Beacon scanner - daemon thread
beacon_config = [
    "c6:ed:e7:7d:e2:e7",
    "fb:d8:50:13:11:46"
  ]


class beacon:
    """
    A simple class to represent a Bluetooth Beacon.
    """
    def __init__(self, addr):
        """
        Constructs all the necessary attributes for the Beacon object.

        Parameters
        ----------
            addr : str
                MAC address of the Bluetooth Beacon.
        """
        self.addr = addr
        self.rssi = 0
        self.lastSeen = None

    def setRssi(self, rssi):
        """
        Sets the latest RSSI value.

        Parameters
        ----------
            rssi : float
                The RSSI of the beacon

        Returns
        -------
        None
        """
        self.rssi = rssi
        self.lastSeen = datetime.now()
        print('Beacon: {}, {}dBm, last seen: {}'.format(
            self.addr,
            self.rssi,
            self.lastSeen))

    def getAddr(self):
        """
        Gets the MAC address of the Bluetooth Beacon.

        Parameters
        ----------
        None

        Returns
        -------
        MAC address of the Bluetooth Beacon : str
        """
        return self.addr

    def getRssi(self):
        """
        Gets the RSSI of the Bluetooth Beacon.

        Parameters
        ----------
        None

        Returns
        -------
        RSSI of the Bluetooth Beacon : int
        """
        return self.rssi

    def getLastSeen(self):
        """
        Gets the time and date the beacon was last seen.

        Parameters
        ----------
        None

        Returns
        -------
        Time and date the beacon was last seen : datetime
        """
        return self.lastSeen


class beaconScanner (threading.Thread):
    """
    A simple class to handle scanning for Bluetooth Beacons.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Beacon Scanner object.

        Parameters
        ----------
        None
        """
        threading.Thread.__init__(self)

    def run(self):
        """
        Constructs a bluepy BTLE scanner and scans indefinately for Bluetooth
        Beacons. If a known beacon is found, the RSSI value is updated.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        while 1:
            scanner = Scanner()
            devices = scanner.scan(5.0)
            for dev in devices:
                lock.acquire()
                for beacon in beacons:
                    if dev.addr == beacon.getAddr():
                        beacon.setRssi(dev.rssi)
                lock.release()


beacons = []
for entry in beacon_config:
    thisBeacon = beacon(entry)
    beacons.append(thisBeacon)

lock = threading.Lock()
t = beaconScanner()
t.daemon = True
t.setDaemon(True)
t.start()

# Web server - main thread
routes = web.RouteTableDef()


@routes.get('/')
async def get_beacons(request):
    lock.acquire()
    response = {}
    for beacon in beacons:
        values = {
            "rssi": beacon.getRssi(),
            "lastSeen": "{}".format(beacon.getLastSeen())}
        response[beacon.getAddr()] = values
    lock.release()
    return web.json_response(response)

app = web.Application()
app.add_routes(routes)
web.run_app(app)
