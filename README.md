# Setup
* python >v3.10 required
* create virtual env
```commandline
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

# Run
### Database
```commandline
docker build -t ratestask .
docker run -p 0.0.0.0:5432:5432 --name ratestask ratestask
```

### Server
```commandline
python -m server
```



### Sample Request
```commandline
curl --request GET \
  --url 'http://localhost:8080/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main'
```

### Notes
* server runs on localhost, port 8080
* it uses the test dockerfile and database from the assignment
* requires environment variables found in `.env` file
* this solution assumes a region and port can have only one parent region
  (a safe assumption given they are primary keys in their tables)
* it also distinguishes between port codes and region slugs by checking `isupper()`, where `True` indicates port
* indexes should be added in the database (these indexes have been added to the `rates.sql` file)
  * on the `parent_slug` field on the `ports` table
  * on the `parent_slug` field on the `regions` table
  * on the `(orig_code, dest_code, day)` fields on the `prices` table
```
CREATE INDEX ports_parent_slug_idx ON ports (parent_slug);
CREATE INDEX regions_parent_slug_idx ON regions (parent_slug);
CREATE INDEX prices_orig_code_dest_code_day_idx ON prices (orig_code,dest_code,"day");
```

# Test
```commandline
python -m unittest -v
```