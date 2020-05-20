"""
Connect to multiple scanners and track beacon location.
"""

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
    def __init__(self, scanner):
        self.name, self.addr = scanner
        self.thread = beaconTracker(self.addr, self.name)
        self.thread.daemon = True
        self.thread.setDaemon(True)
        self.thread.start()

    def getAddr(self):
        return self.addr

    def getName(self):
        return self.name


class beacon():
    def __init__(self, addr):
        self.addr = addr
        self.location = None
        self.scanners = {}

    def addScanner(self, name, addr):
        self.scanners[addr] = {"name": name}

    def printDebug(self):
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
        return self.scanners

    def setLocation(self, location):
        self.location = location

    def getAddr(self):
        return self.addr

    def setScannerData(self, name, addr, rssi, lastSeen):
        self.scanners[addr]['rssi'] = rssi
        self.scanners[addr]["lastSeen"] = lastSeen
        self.printDebug()


class beaconTracker (threading.Thread):
    def __init__(self, addr, name):
        threading.Thread.__init__(self)
        self.addr = addr
        self.name = name

    def run(self):
        while 1:
            self.lastResponse = requests.get(
                "http://{}:8080/".format(self.addr))
            self.processResponse()
            sleep(5)

    def processResponse(self):
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
