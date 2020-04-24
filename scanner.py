"""
Scan for specific beacons and provide and HTTP API to query RSSI
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
    def __init__(self, addr):
        self.addr = addr
        self.rssi = 0
        self.lastSeen = None

    def setRssi(self, rssi):
        self.rssi = rssi
        self.lastSeen = datetime.now()
        print('Beacon: {}, {}dBm, last seen: {}'.format(
            self.addr,
            self.rssi,
            self.lastSeen))

    def getAddr(self):
        return self.addr

    def getRssi(self):
        return self.rssi

    def getLastSeen(self):
        return self.lastSeen


class beaconScanner (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
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
