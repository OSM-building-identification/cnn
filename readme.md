## Building Identification CNN
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery"

### Setup/Installation
 - **python dependencies (pip install \*):**
   - `pyproj` python proj4 implementation for converting between coordinate systems
   - `Pillow` python image maniulation library for working with training images
   - `psycopg2` postgres python lobrary
   - `Flask` simble webserver lib
   - `flask-cors` allows cross origin requests with flask
   - `flask_httpauth` simple http auth module
   - `pandas` data analysis
   - `tensorflow` machine learning
   - `keras` simplified ML api
   - `h5py` reads weight files
 - **credentials file:** the private file `cred.json` is expected in the root directory of this project. It contains information for authenticating to various services. It is not in this repo and should not be added to it.
 - **systemd services** for running jobs continuously
   - `capstone.service` runs the webserver + misc jobs
   
     ~~~
        [Unit]
        Description=CU Capstone ft Trimble Server
        After=network.target

        [Service]
        User=ubuntu
        Group=ubuntu
        WorkingDirectory=/home/ubuntu/
        Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"
        Environment="FLASK_APP=/home/ubuntu/index.py"
        ExecStart=/usr/local/bin/flask run
     ~~~
   - `scanner.service` continuous scanner service
   
     ~~~
        [Unit]
        Description=Tile Scanner
        After=network.target

        [Service]
        User=ubuntu
        Group=ubuntu
        WorkingDirectory=/home/ubuntu/building-identification
        Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"
        ExecStart=/usr/bin/python util/scan.py -105.2752 40.0130
     ~~~

 - **nginx reverse proxy**
   - proxies all incoming traffic at /api to localhost:5000 (flask server)
   - statically servers /home/ubuntu/html at /
   - config:
  
  ~~~
    server {
        listen 80;

        proxy_redirect           off;
        proxy_set_header         X-Real-IP $remote_addr;
        proxy_set_header         X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header         Host $http_host;

        root /home/ubuntu/html;
        index index.html;

        location /  {
          try_files $uri $uri/ =404;
        }

        location /api/ {
            proxy_pass http://api/;
        }

        location ~ /.well-known {
          allow all;
        }

    }
  ~~~
 - **database setup**
  - postgres database, schema is saved in schema.dump
  - create database `cucapstone`:
   - login via `psql`
   - `CREATE DATABASE cucapstone;`
  - being in table schemas `psql -d cucapstone -1 -f schema.dump`
 - **creating database dump**
  - ssh into capstone ec2 then run:  `pg_dump --no-privileges --no-owner --schema-only -h __your_host_here__ -U cucapstone cucapstone`
  
### Webserver (aws only)
webserver is in `building-identification/server/`:

 - serves predictions
 - serves unverified tranining data
 - accepts input on unverified training data

check service status:

 - `sudo service capstone status` check logs for webserver
 - `sudo service capstone restart` restart webserver (after applying changes)
 - `sudo service capstone start` start server after being stopped
 - `sudo service capstone stop` stop server (if going to develop) 
 
run webserver manually:

 - make sure service is stopped
 - `export FLASK_APP=/home/ubuntu/building-identification/server/index.py`
 - `flask run`


### Training Data Prep
 - running `python util/trainingData.py -105.01 40.01 -105 40` fetches all the tiles in the bounding box defined by the top left / bottom right ln,lat points (-105.01, 40.01) and (-105, 40), and uses osm data to check if there are buildings in each tile. It will upload to the training_tiles table in the database. Images are stored in '../tiles'
 - `python util/selectData.py` will take all training data in the database and split it into train and test data and make folders in `./data` with sub folders true and false for use by keras when training

### Classifier Training (anywhere)
 - `python classifier/train.py` looks for source input at `./data` and trains the model on those images (classified by subdirectory). Run the training data prep to get this data. Will save `wights{n}.h5` in the current directory at each epoch.
 - `python classifier/predict.py` tests the model on validation data and shows tiles that it classified wrong. (for degugging purposes)
 - `python classifier/predict.py` creates a visualization of some filter in the network

### Scanner (aws only)
 - given a start point looks for unknown tiles near existing osm data and makes predictions about them if they have no predictions yet and are not in osm data. Saves predictions into the 'predictions' table.
 - `python util/scan.py -105.2752 40.0130` would scan around boulder
