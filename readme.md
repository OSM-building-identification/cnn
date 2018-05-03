# Building Identification From Satelite Imagery
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery" (BIFSI)

## Contents
 - [Architecture Overview](#architecture-overview)
 - [Installation](#installation)
   - [Local-Dev-Specific Installation](#local-dev-specific-installation)
   - [Production-Specific Installation](#production-specific-installation)
 - [Running BIFSI](#running-bifsi)
   - [Training the Image Tile Classifier](#training-the-image-tile-classifier)
   - [Scanning for Missing Buildings](#scanning-for-missing-buildings)
   - [Training the Image Segmentation FCN](#training-the-image-segmentation-fcn)
   - [Using iD](#using-id)
   - [Unit Tests](#unit-tests)
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

 - **install python 2.7 and dependencies:** 

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
 - **install postgres** If you plan to host a local development version of the database, install postress on your local machine. [Instructions here](https://www.postgresql.org/download/) 
 - **setup database schema** the `./schema.dump` file contains the sql commands neccecary to setup the BIFSI database. Create a database for use by BIFSI, then `psql -h your_database_host -d your_database_name your_postgres_username -1 -f schema.dump`. Or connect and run the commands manually.
 - Include the `./data` folder with training data and weights

### Local Dev-Specific Installation
follow these steps in addition to the core [installation](#installation) to setup BIFSI on your local machine:

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
 - start the BIFSI Flask server
   - navigate to your `building-identification` directory
   - find the absolute path of server/index.py. something like `/home/dev/building-identification/server/index.py`
   - `export FLASK_APP=your_absolute_path`
   - `flask run` starts the server
 
### Production-Specific Installation
follow these steps in addition to the core [installation](#installation) to setup BIFSI on a production (remote) machine:

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

## Running BIFSI

### Training the Image Tile Classifier
Note this step is not required since the `./data` folder already has pre-trained weights for the classifier, along with the training data used. Follow these steps if you wish to re-train the classifier on new data.

 - **Gathering new Training Data** 
   - **fetch image tiles:** downloads random tile in an area and sorts them using existing OSM data:
     - run `python classifier/getTrainingData.py -105 39 -104 40` fetches training data in the box between (-105˚w, 39˚n) and (-104˚w, 40˚n). 
     - The coordinate order `is left lng, bottom lat, right lng, top lat`. 
     - Image tiles will be downloaded into `./data/tiles`. 
     - The tile coordinates will be saved into the BIFSI database's `training_tiles` table.
   - **verify image tiles:** Before the training data can be used, it must be verified by hand. This is done with the [manual-verifier](https://github.com/trimble-osm-capstone/manual-verifier). See it's README for usage details.
   - **export data for use:** After the manual-verifier has been used, the records in the `training_tiles` table will have correct values, indicating if each tile has a building in it or not. This step exports the validated data for use in training.
     - run: `python classifier/selectData.py`. 
     - The training data will be saved in `./data/train_classifier/`
 - **Training the CNN** 
   - **fit the model:** once training data is available in `./data/train_classifier/` you can train the network to fit this data: 
     - run `python classifier/train.py` to train the network. 
     - Each epoch, weights will be saved at `./data/weights/classifier%d.h5`. 
     - If you wish to train from starting weights use: `python classifier/train.py -w path/to/your/weights.h5`
   - **test the model:** after a model has been trained you can test its performance.
     - run `python classifier/test.py -w path/to/your/weights.h5`
     -  Any failing images will be shown for diagnostic purposes. 
   
### Scanning for Missing Buildings
This is the process of using BIFSI's CNN tile classifier to search an area for tiles that have buildings in real life, but not in OSM. There are two strategies that can be used, when scanning an area:

 - **Quadtree scanning**: recursively subdivide the area and ignore quadrants that do not already have osm data. When quadrants are sufficently small, scan them exhaustively. This assumes that missing buildings are likely to be near buildings that are already in OSM.
 - **Road Scanning**: find all roads within a given area, then find the tiles near the road. This is useful in places where there is not very much OSM building data, but there is good OSM road data.
 - **usage** `python classifier/scan.py (roads|quads) left bottom right top` 
   - scan with quads: `python classifier/scan.py quads -105 39 -104 40`
   - scan with roads: `python classifier/scan.py roads -105 39 -104 40`
 - **output**: predictions will be saved in BIFSI's database in the `predictions` table. They will ve visible when using our version of [iD](https://github.com/trimble-osm-capstone/iD) as clusters of white tiles.

### Training the Image Segmentation FCN
This is not required to run BIFSI, since the FCN has already been trained on NAIP imagery. Proceed if you want to train on different imagery, or want to improve the FCN by finding more data.

 - **Gathering new Training Data** 
   - **fetch image tiles:** this is the process of downloading image tiles where OSM alrady has data, and using that osm data to make a black and white mask of where the buildings are.
     - run `segmentation/getTrainingData.py -105 39 -104 40` to fetch tiles between (-105,39) and (-104,40).
     - Tiles will be saved in `./data/tiles` masks will be saved in `./data/masks`
     - The coordinates of the tiles will be saved in the `segmentation_training_tiles` table.
   - **correcting/validating data:** after the raw data has been downloaded, it must be corrected for imagery offsets, and checked for missing buildings. This is done with the [manual-verifier](https://github.com/trimble-osm-capstone/manual-verifier). See it's README for usage details.
   - **export data for use:** After the data has been corrected and validated, it can now be exported into the data directory, ready to train.
     - run `python segmentation/selectData.py`
     - images and masks will be aligned and saved in `./data/train_segmentation/`
 - **Training the FCN** 
   - **fit the model:** once training data is available in `./data/train_segmentation/` you can train the network to fit this data: 
     - run `python segmentation/train.py` to train the network. 
     - Each epoch, weights will be saved at `./data/weights/c segmentation%d.h5`. 
     - If you wish to train from starting weights use: `python segmentation/train.py -w path/to/your/weights.h5`
     - Note this model is much more complex then the simple CNN, and it will take a very long time to train.
   - **test the model:** once the model is trained you can test it on images to evaluate its performance.
     - run `python segmentation/test.py -w path/to/your/weights.h5`
     - image masks will be shown
     - original image with estimated contours will be show as well

### Using iD
Our modified version of the iD editor serves two purposes:

 - Show the results of the [scan](#scanning-for-missing-buildings)
 - Use the Image segmentation FCN to predict building contours automatically.
 - Make sure the BIFSI flask server is running, then see the [iD instructions](https://github.com/trimble-osm-capstone/iD) for more details.

### Unit tests
to run unit tests, run `python tests/test_suite.py`


## File Structure

 - `classifier` all scrips for tile classification
    - `cnn.py` keras structure definition for the CNN model
    - `train.py` handles reading training data, training the network
    - `getTrainingData.py` generates training data
    - `selectData.py` exports training data after it is validated
    - `test.py` evaluates the model
 - `segmentation` image segmentation model and helpers
    - `fcn.py` keras srtucture of FCN model
    - `train.py` reads traning data, augments it, trains model
    - `getTrainingData.py` automatically generates training data
    - `selectData.py` exports training data after it is validated
    - `test.py` uses model to predict contours on image tiles
    - `predict.py` mask prediction, contour estimation functions
 - `server` flask server for iD and manual-verifier
    - `index.py` entry point, sets up flask, authentication, loads routes
    - `db.py` setus up database connection for server
    - `tileServer.py` serves tiles from *data/tiles* for use by manual verifier
    - `missingTiles.py` serves clusters of tiles output from scanning
    - `manualVerifier.py` accepts user input from manual verifier to mark tiles as valid/invalid
    - `contourPredictor.py` on demand image segmentation for a tile in iD
    - `dbProxy.py` proxies OSM db requests for local dev machines
 - `util/` helper scripts
    - `db.py` sets up db connections for training data gathering/exporting
    - `cred.py` reads *cred.json* and parses it as json
    - `imagery.py` gets tileserver urls and, has function to download specific tiles
    - `tileMath.py` converting tile coordinates to degrees and related functions
    - `contourMath.py` linalg helper functions for contour estimation
 - `tests/` unit tests
    - `test_suite.py` runs entire test suite
    - `test_scan.py` tests for scanning utilities, roads quatrees etc
    - `test_tileMath.py` tests for tile math utils
 - `schema.dump` database schema for creating new db
 - `cred.json` **not in repo** contains credentials for databases, http auth, api keys etc
 - `data/` **not in repo** contains all data for use by models
    - `weights/` pre-trained weights
        - `classifier.h5` weights for classifier CNN
        - `segmentation.h5` weights for image segmentation FCN
    - `tiles/` image tiles
    - `masks/` masks generated automaticlaly from OSM data
    - `train_classifier/` cleaned and ready classifier training data
    - `train_segmentation/` clean data for image segmentation, includes tiles and masks.
