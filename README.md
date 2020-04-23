# Beacon Tracker

This Python project consists of multiple scanner elements (intended to run on RPi) and a single co-ordinator element.

Beacon position is triangulated based on the position of the scanners.

## Scanner

Run on a RPi with bluetooth.

Depends on [bluepy](https://pypi.org/project/bluepy/).

Usage:
```bash
sudo -E python3 scanner.py
```

Head to http://\<RPi IP Address\>:8080/beacons/