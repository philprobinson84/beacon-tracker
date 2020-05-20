"""Connect to multiple scanners and track beacon location."""

import threading
import requests
from time import sleep
from aiohttp import web

beacon_config = [
    "c6:ed:e7:7d:e2:e7",
    "fb:d8:50:13:11:46"
]

scanner_config = [
    {"hall": "192.168.1.85"},
    {"lounge": "192.168.1.185"},
    {"dining": "192.168.1.171"}
]


class tracker():
    """
    A simple class to represent a scanner.
    """
    def __init__(self, scanner):
        """
        Constructs all the necessary attributes for the tracker object.

        Parameters
        ----------
            scanner : str
                IP address of the scanner.
        """
        self.name, self.addr = scanner
        self.thread = beaconTracker(self.addr, self.name)
        self.thread.daemon = True
        self.thread.setDaemon(True)
        self.thread.start()

    def getAddr(self):
        """
        Gets the IP address of the scanner.

        Parameters
        ----------
        None

        Returns
        -------
        IP address of the scanner : str
        """
        return self.addr

    def getName(self):
        """
        Gets the name of the scanner.

        Parameters
        ----------
        None

        Returns
        -------
        Name of the scanner : str
        """
        return self.name


class beacon():
    """
    A simple class to represent a beacon.
    """
    def __init__(self, addr):
        """
        Constructs all the necessary attributes for the beacon object.

        Parameters
        ----------
            addr : str
                MAC address of the Bluetooth Beacon.
        """
        self.addr = addr
        self.location = None
        self.scanners = {}

    def addScanner(self, name, addr):
        """
        Adds a scanner.

        Parameters
        ----------
            name : str
                Name of the scanner.
            addr : str
                IP address of the scanner.
        """
        self.scanners[addr] = {"name": name}

    def printDebug(self):
        """
        Prints debug information.

        Parameters
        ----------
        None
        """
        print('''
BEACON: {}
=============================
Scanners:
{}
        '''.format(
            self.addr,
            self.scanners
        ))

    def getScanners(self):
        """
        Gets a list of scanners.

        Parameters
        ----------
        None

        Returns
        -------
        list of scanners : list of str
        """
        return self.scanners

    def setLocation(self, location):
        """
        Sets the location of the scanner.

        Parameters
        ----------
            location : str
                location of the scanner, typically a room name.

        Returns
        -------
        None
        """
        self.location = location

    def getAddr(self):
        """
        Gets the MAC address of the Beacon.

        Parameters
        ----------
        None

        Returns
        -------
        MAC address of the Bluetooth Beacon.
        """
        return self.addr

    def setScannerData(self, name, addr, rssi, lastSeen):
        """
        Updates the beacon with latest scanner data.

        Parameters
        ----------
            name : str
                Name of the scanner.
            addr : str
                IP address of the scanner.
            rssi : int
                RSSI of the beacon.
            lastSeen : datetime
                Time and date the beacon was last seen by the scanner.

        Returns
        -------
        None
        """
        self.scanners[addr]['rssi'] = rssi
        self.scanners[addr]["lastSeen"] = lastSeen
        self.printDebug()


class beaconTracker (threading.Thread):
    """
    Simple class to intended to run as a thread within a tracker object.
    """
    def __init__(self, addr, name):
        """
        Constructs all the necessary attributes for the tracker thread.

        Parameters
        ----------
            addr : str
                IP address of the scanner.
            name : str
                Name of the scanner.
        """
        threading.Thread.__init__(self)
        self.addr = addr
        self.name = name

    def run(self):
        """
        Main loop, one for each scanner.
        Get scan results every 5s and process the response.
        """
        while 1:
            self.lastResponse = requests.get(
                "http://{}:8080/".format(self.addr))
            self.processResponse()
            sleep(5)

    def processResponse(self):
        """
        Process the response from the scanner and updated beacon objects
        accordingly.
        """
        for beacon in beacons:
            json = self.lastResponse.json()
            if json[beacon.getAddr()]['rssi'] != 0:
                beacon.setScannerData(
                    self.name,
                    self.addr,
                    json[beacon.getAddr()]['rssi'],
                    json[beacon.getAddr()]['lastSeen'])


scanners = []
for entry in scanner_config:
    thisScanner = tracker(entry.popitem())
    scanners.append(thisScanner)

beacons = []
for entry in beacon_config:
    thisBeacon = beacon(entry)
    for scanner in scanners:
        thisBeacon.addScanner(scanner.getName(), scanner.getAddr())
    beacons.append(thisBeacon)

# Web server - main thread
routes = web.RouteTableDef()


@routes.get('/')
async def get_beacons(request):
    response = {}
    for beacon in beacons:
        response[beacon.getAddr()] = beacon.getScanners()
    return web.json_response(response)

app = web.Application()
app.add_routes(routes)
web.run_app(app, port=8081)
