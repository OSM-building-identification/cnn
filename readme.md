## Building Identification CNN
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery"

### Setup/Installation
 - **python dependencies:**
   - `pyproj` python proj4 implementation for converting between coordinate systems `pip install proj4`
 - **credentials file:** the private file `cred.json` is expected in the root directory of this project. It contains information for authenticating to various services. It is not in this repo and should not be added to it.

### Training Data Prep
running `python util/trainingData.py` fetches all the tiles in the bounding box defined in that file, and uses osm data to check if there are buildings in each tile. It will produce two folders `./True` (has building(s)) and `./False` no buildings. `./False` must be manually checked since it is very likely that tiles where osm data is missing will be included resulting in a false negative.
