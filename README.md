# AISExplorer

## Installation

```
pip install aisexplorer
```

## Usage

### Find vessel by MMIS

```
import aisexplorer

from ais_explorer.AIS import get_location

get_location(211281610)
```

### Find vessels in Area

```
import aisexplorer

from ais_explorer.AIS import get_area_data

get_area_data("EMED", return_df= True)
```
Output is limited to 500 rows.
[Areas](https://help.marinetraffic.com/hc/en-us/articles/214556408-Areas-of-the-World-How-does-MarineTraffic-segment-them-) can be found here

## Next Steps

Add filters to Area Function
Add docstrings to functions






