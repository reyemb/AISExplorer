# AISExplorer  

![PyPI](https://img.shields.io/pypi/v/AISExplorer)
![PyPI - Downloads](https://img.shields.io/pypi/dm/AISExplorer)
![example workflow](https://github.com/reyemb/AISExplorer/actions/workflows/python-package.yml/badge.svg?style=for-the-badge)

AISExplorer can be used to locate vessels or to scrape all vessel in an specific AREA.
Also free proxies can be used for scraping. Proxies will be scraped from [sslproxies](https://www.sslproxies.org/), tested and used. Also Fallback are implemented

## Installation

``` cmd
pip install aisexplorer
```

## Usage

### Find vessel by MMIS

```python
from aisexplorer.AIS import AIS

AIS().get_location(211281610)
```

### Find vessels in Area

**maximum 500 vessels**

```python
from aisexplorer.AIS import AIS

AIS(return_df= True).get_area_data("EMED")
```

Output is limited to 500 rows.
[Areas](https://help.marinetraffic.com/hc/en-us/articles/214556408-Areas-of-the-World-How-does-MarineTraffic-segment-them-) can be found here

### Get Table via URL

```python
from aisexplorer.AIS import AIS

AIS(return_df = True).get_data_by_url("https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,NaN")
```

### Use Proxies

```python
from aisexplorer.AIS import AIS

AIS(return_df = True, Proxy = True).get_data_by_url("https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,NaN")

```

### Get Data for user created fleets

```python
from aisexplorer.AIS import AIS

AIS(return_df = True, Proxy = True).get_vessels_in_all_fleets()

```

## Next Steps

- Add more potential proxy lists
- Find a way to change the number of retrys
- Reset new filters

## Changelog

### 2023-1-21

- Added logged in functions

### 2021-12-10

- Added Fallback if proxy has died
- Added get data by url
- Added Check if requests was filtered by cloudflare

### 2021-12-5

- Added Filters early stage
- Added Retry Options
- Added some new exceptions

### 2021-11-27

- Added Proxy Option
