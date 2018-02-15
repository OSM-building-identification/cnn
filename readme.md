# Building Identification CNN
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery"

## Setup

### Local Installation
 - **install python2.7 and dependencies:**

    *pip install pyproj Pillow psycopg2 Flask flask-cors
     flask_httpauth pandas tensorflow keras h5py grequests*
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
   - `grequests` async file downloads
 - **credentials file:** the private file `cred.json` is expected in the root directory of this project. It contains information for authenticating to various services. It is not in this repo and should not be added to it. It has the following format: (you will probably have to edit database credentials to be your own)
 -
    ~~~
    {
     "naip_tiles_key" : ... ,
     "osm" : { //this is only required on production server
         "host" : ...,
         "port" : "5432",
          "user" : ...,
          "pass" : ...
     },
     "db" : { //local db connection (for storing predictions, tiles etc)
         "db" : ..., //dm name
        "user" : ..., //postgres user
        "host" : "localhost", //except on server
        "pass" : ...
     },
     "http" : { //http authentication for use on server
          "pass" : ...
     },
     "dev" : "true" //set to true execpt on production server
    }
    ~~~
 - **postgres setup**
   - install postgresql
   - navigate to `building-identification` directory
   - `psql` or `sudo -u psql` depending on OS
     - `CREATE DATABASE cucapstone;`
   - `psql -d cucapstone -1 -f schema.dump` load table schemas. (will drop existing tables and start fresh)
 - *at this point you should be able to run Training Data Prep*
 - **flask setup**
   - navigate to your `building-identification` directory
   - find the absolute path of server/index.py. something like `/home/dev/building-identification/server/index.py`
   - `export FLASK_APP=your_absolute_path`
 - *at this point you should be able to install and run the manual-verifier and iD*

## Commands


### Training Data Prep
 - `python util/trainingData.py -105.1 40 -105 40.1` fetches all the tiles in the bounding box defined by the coordinates in order `left bottom right top`, and uses osm data to check if there are buildings in each tile. It will upload to the training_tiles table in the database. Images are stored in `data/tiles`
 - `python util/selectData.py` will take all training data in the database and split it into train and test data and make folders in `./data` with sub folders true and false for use by keras when training. NOTE this only uses tiles that are marked in the database as verified.

### Classifier Training (anywhere)
 - `python classifier/train.py` looks for source input at `./data` and trains the model on those images (classified by subdirectory). Run the training data prep to get this data. Will save `wights{n}.h5` in the current directory at each epoch.
 - `python classifier/predict.py` tests the model on validation data and shows tiles that it classified wrong. (for degugging purposes)
 - `python classifier/visual.py` creates a visualization of some filter in the network

### Scanner
 - given a start point looks for unknown tiles near existing osm data and makes predictions about them if they have no predictions yet and are not in osm data. Saves predictions into the 'predictions' table.
 - `python util/scan.py -105.2752 40.0130` would scan around boulder

## Production Setup (aws only)
in addition to all other setup steps
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
 - **creating database dump**
  - ssh into capstone ec2 then run:  `pg_dump --no-privileges --no-owner --clean --schema-only -h __your_host_here__ -U cucapstone cucapstone`
 - **running webserver**
   - `sudo service capstone status` check logs for webserver
   - `sudo service capstone restart` restart webserver (after applying changes)
   - `sudo service capstone start` start server after being stopped
   - `sudo service capstone stop` stop server (if going to develop)

### Webserver via Systemd (aws only)
webserver is in `building-identification/server/`:

 - serves predictions
 - serves unverified tranining data
 - accepts input on unverified training data

check service status:
