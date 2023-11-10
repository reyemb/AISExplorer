# AISExplorer  

![PyPI](https://img.shields.io/pypi/v/AISExplorer)
![PyPI - Downloads](https://img.shields.io/pypi/dm/AISExplorer)
![example workflow](https://github.com/reyemb/AISExplorer/actions/workflows/python-package.yml/badge.svg?style=for-the-badge)

AISExplorer is a tool for locating vessels or scraping vessel data in a specific area. However, due to recent updates, the use of free proxies, previously scraped from sources like [sslproxies](https://www.sslproxies.org/), has been discontinued due to errors such as 403 Forbidden responses.

## Next Steps

- Explore additional sources for proxy lists.
- Implement a method to customize the number of retries.
- Introduce functionality to reset filters.

## Changelog

### 2023-11-10

  - Due to Captcha implementation, login functionality is broken.
  - Sending requests through proxies now leads to a 403 error; proxy support has been removed.

### 2023-1-21

- Integrated login functions for additional features.

### 2021-12-10

- Implemented fallback if a proxy fails.
- Introduced the ability to retrieve data directly via URL.
- Added checks for Cloudflare's filtering mechanisms.

### 2021-12-5

- Early stages of filter implementation.
- Retry options were added for resilience.
- New exceptions were introduced for better error handling.

### 2021-11-27

- Proxy support was added (discontinued as of 2023-11-10).

## Installation

``` cmd
pip install aisexplorer
```

## Usage

### Find vessel by MMIS
Retrieve the current location of a vessel using its MMSI identifier.

```python
from aisexplorer.AIS import AIS

AIS().get_location(211281610)
```

### Find vessels in Area
Retrieve data for up to 500 vessels within a designated area.

**maximum 500 vessels**

```python
from aisexplorer.AIS import AIS

AIS(return_df= True).get_area_data("EMED")
```

The output is limited to 500 rows. Area codes can be referenced from the MarineTraffic help section.
[Areas](https://help.marinetraffic.com/hc/en-us/articles/214556408-Areas-of-the-World-How-does-MarineTraffic-segment-them-) can be found here

### Get Table via URL
Directly access table data using a MarineTraffic URL.

```python
from aisexplorer.AIS import AIS

AIS(return_df = True).get_data_by_url("https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,NaN")
```

### Use Proxies

Previously, AISExplorer allowed fetching data using proxies for anonymization. This feature is no longer supported due to compatibility issues with the data source.

### Get Data for user created fleets

No longer available as it required user login, which is now deprecated due to captcha implementation.

