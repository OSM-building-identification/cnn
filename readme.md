# Building Identification CNN
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery" (BIFSI)

## Contents
 - [Architecture Overview](#architecture-overview)
 - [Installation](#installation)
   - [Local-Dev-Specific Installation](#installation)
   - [Production-Specific Installation](#production-specific-installation)
 - [Tile Classification](#tile-classification)
   - [Gathering Data](#gathering-classification-data)
   - [Verifying Data](#verifying-classification-data)
   - [Training](#training-classifier)
   - [Testing](#testing-classifier)
   - [Scanning](#scanning-for-missing-buildings)
 - [Tile Segmentation](#tile-segmentation)
   - [Gathering Data](#gathering-segmentation-data)
   - [Verifying Data](#verifying-segmentation-data)
   - [Training](#training-segmentation-network)
   - [Testing](#testing-segmentation-network)
 - [File Structure](#file-structure)
 
## Architecture Overview
BIFSI is split across 3 repositories:
 - [building-identification](https://github.com/trimble-osm-capstone/building-identification) (this repo): contains all python machine learning, and the server side for the other repos
 - [manual-verifier](https://github.com/trimble-osm-capstone/manual-verifier): helper application for internal use, allows quick verification of training data.
 - [iD](https://github.com/trimble-osm-capstone/iD): Fork of the OSM editor [iD](https://github.com/openstreetmap/iD) that displays where missing buildings can be found, and can import contour predictions from the server side.

BIFSI Relies on the following data sources:
 - the `./data` folder to be included at the top level of this repo, includes training data images, as well as trained model weights
 - `./cred.json` includes credentials data used for accessing resources such as image tiles, and databases
 - *postgres* database for storing the current state of training data, scans, and predictions.
 - *postgres* database with a mirror of OSM's data
 
BIFSI is intended to be run both locally (on a developer's machine) and in production on a linux server. Its behavior is exactly the same in both cases, except for its database connections:
 - In production both the OSM mirror and the BIFSI database are expected to be remote servers, whose credientials are configured in `cred.json`
 - In local development the BIFSI database can be running locally (also configured in `cred.json`), but the OSM database may not be accessed directly, since RDS can only be connected to from AWS's subnet. Instead, the local version of BIFSI will proxy its OSM requests to a production version running in AWS, whose location is configured in `cred.json`. If there is no rmote instance of BIFSI's flask server running on aws, features needing access to OSM will not be available, but everything else will still work.

## Installation
These installation steps are required both locally and in production:
 - **install python2.7 and dependencies:** 

    *pip install pyproj Pillow psycopg2 Flask flask-cors
     flask_httpauth pandas tensorflow keras h5py grequests opencv-python* 
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
   - `opencv-python` computer vision utilities
 - **flask setup**
   - navigate to your `building-identification` directory
   - find the absolute path of server/index.py. something like `/home/dev/building-identification/server/index.py`
   - `export FLASK_APP=your_absolute_path`
 - **install postgresql ~9.6** [here](https://www.postgresql.org/) make sure you can connect to your BIFSI database.
 - **setup database** the `./schema.dump` file contains the sql commands neccecary to setup the BIFSI database. Create a database for use by BIFSI, then `psql -h your_database_host -d your_database_name your_postgres_username -1 -f schema.dump`. Or connect and run the commands manually.
 - Include the `./data` folder with training data and weights

### Local-Dev-Specific Installation
 - Inclide a `cred.json` for local development. It should have the following structure:
 
  ~~~
    {
     "naip_tiles_key" : ... , 
     "db" : { //BIFSI db connection (for storing predictions, tiles etc)
        "db" : ..., //dm name
        "user" : ..., //postgres user
        "host" : ..., //probably localhost
        "pass" : ...
     },
     "http" : { 
        "pass" : ..., //http authentication password to protect server
        "remote-host" : ... //address of server running BIFSI (for proxying osm DB requests)
     },
     "dev" : "true"
    }
  ~~~
  
 - **Make sure** you have an instance of BIFSI running remotely, and its address in `cred.json`'s http.remote-host key.
 
### Production-Specific Installation
 - Inclide a `cred.json` for Production. It should have the following structure:
 
  ~~~
    {
     "naip_tiles_key" : ... , 
     "db" : { //BIFSI db connection (probably an RDS instance)
        "db" : ..., //dm name
        "user" : ..., //postgres user
        "host" : ..., //probably
        "pass" : ...
     },
     "osm" : { //OSM mirror db credentials
         "host" : ...,
         "port" : "5432",
         "user" : ...,
         "pass" : ...
     },
     "http" : { 
        "pass" : ... //http authentication password to protect server
     },
     "dev" : "false"
    }
  ~~~
- **setup systemd service** for running the BISFI server continuously
   - create the file `/etc/systemd/system/capstone.service` runs the webserver + misc jobs
   
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

 - **setup nginx reverse proxy**
   - proxies all incoming traffic at /api to localhost:5000 (flask server)
   - statically servers /home/ubuntu/html at /
   - make sure nginx is installed
   - config file at `/etc/nginx/sites-enabled/your_host_ip`:
  
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
   - then run `sudo service nginx restart` to restart nginx with the new config
  
- *start BIFSI*: `sudo service capstone start`

## Tile Classification

### Gathering Classification Data

### Verifying Classification Data

### Training Classifier

### Testing Classifier

### Scanning For Missing Buildings

## Tile Segmentation

### Gathering Segmentation Data

### Verifying Segmentation Data

### Training Segmentation Network

### Testing Segmentation Network

## File Structure

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
