# DRF Auto

Simple DRF API creation tool. Generate serializers, views, and URLs from models.py.

---

## Usage

* Generate all files (`serializers.py`, `views.py`, and `urls.py`)
```PowerShell
python drf-auto.py models.py
```
* Generate serializers only
```PowerShell
python drf-auto.py models.py -s
```
* Generate views only
```PowerShell
python drf-auto.py models.py -v
```
* Generate URLs only
```PowerShell
python drf-auto.py models.py -p
```
