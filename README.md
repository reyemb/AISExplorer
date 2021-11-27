# AISExplorer
AISExplorer can be used to locate vessels or to scrape all vessely in an AREA

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

**maximum 500 vessels**

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

## Changelog

### 2021-11-27

- Added Proxy Option






