# Beacon Tracker

This Python project consists of multiple scanner elements (intended to run on RPi) and a single co-ordinator element.

Beacon position is triangulated based on the position of the scanners.

## Scanner

Run on a RPi with bluetooth.

Depends on [bluepy](https://pypi.org/project/bluepy/).

Usage:

Replace lines 12 & 13 with the beacon MAC addresses you wish to track, then:

```bash
sudo python3 scanner.py
```

Head to `http://\<RPi IP Address\>:8080/`

## Tracker

Run anywhere you can run Python, typically on one of the scanners.

Usage:

Replace lines 12 & 13 with the beacon MAC addresses you wish to track, replace lines 16 to 18 with your trackers, then:

```bash
python3 tracker.py
```

Head to `http://\<RPi IP Address\>:8081/`