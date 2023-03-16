# Setup
* python v3.10
* create virtual env
```commandline
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```
# Notes
* this solution assumes a region and port can have only one parent region
  (a safe assumption given they are primary keys in their tables)
* it also distinguishes between port codes and region slugs by checking isupper(), where True means port
# Run
```commandline
python -m server.py
```

# Test
```commandline
python -m unittest -v Test
```
