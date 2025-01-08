

import argparse
import calendar
import datetime
import json
import sys

import jsonschema
import pandas as pd

DATE_FORMAT = "%Y-%m-%d"


def string_to_date(d: str, f: str = DATE_FORMAT, old_format=None) -> datetime.date:
    # To convert the old STATE date format "YYYY-MM-DD" to the new format "YYYYMMDD" we need this `old_format` additional param.
    # As soon as all current cloud sync will be converted to the new format we can remove this double format support.
    if not d: return None
    if old_format:
        try:
            return datetime.datetime.strptime(d, old_format).date()
        except ValueError:
            pass
    return datetime.datetime.strptime(d, f).date()


def date_to_string(d: datetime.date, f: str = DATE_FORMAT) -> str:
    return d.strftime(f)

def get_dimensions(source):
    dimensions_dict = {
        "adstats-publisher": ["channel", "dealCode", "supplySeat", "brand", "publisher", "platform",
                              "supplyType", "parentAdvertiser", "supplyDomain", "adSourceEndDate"],
        #                       ["orderId", "year", "parentAdvertiser", "channel", "inventoryLabel",
        #                       "supplySeat", "supply", "industryCode", "adSourceId","adSourceMinDuration",
        #                       "industryId", "appBundleId", "season", "dealCode", "supplyDomain", "brand",
        #                       "adSourceEndDate", "adSourceLabel", "supplyType", "publisher", "platform",
        #                       "platformFamily", "buyerSeatName"],

        "deals-publisher": ["nameInAppStore", "parentAdvertiser", "channel", "supplySeat", "holdingCompany",
                            "supply", "dealDateCreated", "adSourceStatus", "appBundleId", "dealCode",
                            "supplyDomain", "day", "brand", "buyerSeatCode", "adSource", "dealStatus",
                            "dealType", "publisher", "mktStartDate", "supplySeatId", "currency", "dealOrigin",
                            "advertiser", "buyerName", "buyerCode", "pacingType", "dealName",
                            "calculatedMinDuration", "advertiserDomain", "mktEndDate"]
    }
    return dimensions_dict[source]

def get_metrics(source):
    metrics_dict = {
        "adstats-publisher": ["sspNetRevenue", "adsrvFee", "ctr", "operatorCpm", "netCpm", "netProgCpm", "grossProgCpm",
                              "netRevenue", "grossRevenue", "sspGrossRevenue"],
                            # ["sspNetRevenue", "adsrvFee", "testImpressions", "ctr", "useRate", "avgCompletionRate",
                            #   "impsRemaining", "tagUseRate", "discountGrossRevenue", "grossTagRevenue", "requests",
                            #   "operatorCpm", "sspGrossRevenue", "grossProgCpmInclDemandFee", "fee", "fillRate",
                            #   "completionRate", "impressionRate", "netCpm", "netProgCpm", "grossProgCpm",
                            #   "tagFillRate", "netRevenue", "completions", "grossRevenue", "netTagRevenue", "tagFee"],

        "deals-publisher": ["ctr", "netRevenue", "avgFloorPricesPlusDemandFee", "firstQuartiles", "firstQuartilesRate",
                            "bidsLoss", "completions", "impressions", "operatorCost", "grossRevenue", "validBids",
                            "netCpm", "clicks", "secondQuartilesRate", "revenueInclDemandFee", "eligibleBids", 
                            "demandAcquisitionCost"]
    }
    return metrics_dict[source]
