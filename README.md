Electricity Market Prices
=========================

This simple script downloads Day-ahead market prices from the API of
[ENTSOE-E](https://transparency.entsoe.eu/) Transparency Platform.

It then presents hourly market prices together with end user prices for end
users using dynamic energy prices offered by [Zonneplan](https://www.zonneplan.nl/energie). The main purpose is to be able to check whether the prices offered by Zonneplan are correct and to see historical price data.

Installation
------------

You need an API key to access ENTSOE-E Transparency Platform API. Follow
[this guide](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_authentication_and_authorisation)
to get one. Put that key into `market_prices_config.py` and you are done.

Usage
-----

```
$ ./market_prices.py --help
usage: market_prices.py [-h] [-s START] [-e END]

Download and present hourly market prices as well as end user energy prices

options:
  -h, --help            show this help message and exit
  -s START, --start START
                        start date
  -e END, --end END     end date

$ ./market_prices.py --start 20230702 --end 20230703

2023-07-02
Hour    €/MWh  ct/kWh
=====================
00-01   16.45    19.2
01-02    3.17    17.6
02-03    0.01    17.2
03-04    0.00    17.2
04-05   -0.03    17.2
05-06   -0.05    17.2
06-07   -0.06    17.2
07-08   -0.51    17.2
08-09   -2.97    16.9
09-10  -16.90    15.2
10-11  -60.00    10.0
11-12 -252.92   -13.4
12-13 -449.57   -37.2
13-14 -500.00   -43.3
14-15 -500.00   -43.3
15-16 -500.00   -43.3
16-17 -172.39    -3.6
17-18  -35.18    13.0
18-19   -6.01    16.5
19-20    4.88    17.8
20-21   69.10    25.6
21-22   85.58    27.6
22-23   94.90    28.7
23-24   86.08    27.7

