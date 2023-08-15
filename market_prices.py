#!/usr/bin/env python3

import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree
import argparse

from market_prices_config import *

def download_xml(startdate=None, enddate=None, market=market):
    """
    Download XML Market data from the ENTSOE transparency plaform.
    """
    if startdate is None:
        td = datetime.date.today()
        startdate = datetime.datetime(td.year, td.month, td.day, tzinfo=TZ)
    if enddate is None:
        enddate = datetime.timedelta(2) + startdate
    startdate, enddate = [d.astimezone(datetime.timezone.utc)
                          for d in (startdate, enddate)]
    s, e = [f"{d.year:04}{d.month:02}{d.day:02}"
            f"{d.hour:02}{d.minute:02}"
            for d in (startdate, enddate)]

    params = urllib.parse.urlencode({
                "securityToken": token,
                "documentType": "A44",
                "in_Domain": market,
                "out_Domain": market,
                "periodStart": s,
                "periodEnd": e,
        })
    with urllib.request.urlopen(f"{API_URL}?{params}") as url:
        doc = xml.etree.ElementTree.parse(url)
    return doc


def parse_iso_timedelta(timedelta):
    """
    Simplified parser of ISO 8601 interval string.
    Return a timedelta instance.
    Only minutes difference is supported.
    """
    assert timedelta[:2] == "PT", f"String {timedelta} does not start with PT"
    assert timedelta[-1] == "M", f"String {timedelta} does not end with M"
    return datetime.timedelta(minutes=int(timedelta[2:-1]))


def parse_xml_doc(doc):
    """
    Parse ElementTree document with hourly prices.
    Yield (datetime, float) for each data point.
    """
    for per in doc.findall('.//{*}Period'):
        start = per.find("{*}timeInterval/{*}start").text
        resolution = per.find("{*}resolution").text
        delta = parse_iso_timedelta(resolution)
        d = datetime.datetime.fromisoformat(start)
        for pos, val in per.findall("{*}Point"):
            pos = int(pos.text)
            val = float(val.text)
            yield (d+(pos-1)*delta, val)


def get_end_price(marketprice):
    return marketprice/1000 * vat_rate + tax_per_kwh + handling_per_kwh

def print_prices(data):
    """
    Pretty print prices.
    """
    olddate = datetime.date.min
    for dt, price in data:
        dt = dt.astimezone(TZ)
        if dt.date() != olddate:
            olddate = dt.date()
            print()
            print(f"{dt.year:04}-{dt.month:02}-{dt.day:02}")
            print("Hour    €/MWh   ct/kWh")
            print("======================")
        endprice = get_end_price(price)
        print(f"{dt.hour:02}-{dt.hour + 1:02} {price:>7.2f}   "
              f"{100*endprice:>6.2f}")


def datetime_parser(s):
    """
    Parse a string containging YYYYMMDD into a proper timezone-aware
    datetime object of local midnight of that day
    """
    d = datetime.date.fromisoformat(s)
    return datetime.datetime(d.year, d.month, d.day, tzinfo=TZ)


def parse_options():
    parser = argparse.ArgumentParser(
            description="Download and present hourly market prices "
                        "as well as end user energy prices"
    )
    parser.add_argument("-s", "--start", help="start date",
                        metavar="YYYYMMDD", type=datetime_parser)
    parser.add_argument("-e", "--end", help="end date",
                        metavar="YYYYMMDD", type=datetime_parser)
    parser.add_argument("--market", help="market id",
                        default=market)
    return parser.parse_args()


def main():
    args = parse_options()
    doc = download_xml(args.start, args.end, args.market)
    data = parse_xml_doc(doc)
    print_prices(data)


if __name__ == '__main__':
    main()
