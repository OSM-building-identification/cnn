## Building Identification CNN
for Trimble Seinor Capsone Project "Building Identification from Satelite Imagery"

### Setup/Installation
 - **python dependencies:**
   - `pyproj` python proj4 implementation for converting between coordinate systems `pip install proj4`
   - `pillow` python image maniulation library for working with training images `pip install Pillow`
 - **credentials file:** the private file `cred.json` is expected in the root directory of this project. It contains information for authenticating to various services. It is not in this repo and should not be added to it.

### Training Data Prep
running `python util/trainingData.py -105.01 40.01 -105 40` fetches all the tiles in the bounding box defined by the top left / bottom right ln,lat points (-105.01, 40.01) and (-105, 40), and uses osm data to check if there are buildings in each tile. It will produce two folders `./True` (has building(s)) and `./False` no buildings. `./False` must be manually checked since it is very likely that tiles where osm data is missing will be included resulting in a false negative.
