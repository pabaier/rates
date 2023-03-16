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
* indexes should be added in the database
  * on the parent_slug field on the ports table
  * on the parent_slug field on the regions table
  * on the (orig_code, dest_code, day) fields on the prices table
```
CREATE INDEX ports_parent_slug_idx ON ports (parent_slug);
CREATE INDEX regions_parent_slug_idx ON regions (parent_slug);
CREATE INDEX prices_orig_code_dest_code_day_idx ON prices (orig_code,dest_code,"day");
```
# Run
```commandline
python -m server.py
```

# Test
```commandline
python -m unittest -v Test
```
