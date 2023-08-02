:::caution

**The Google Analytics (Universal Analytics) connector will be deprecated soon.**

Google is phasing out Universal Analytics in favor of Google Analytics 4 (GA4). In consequence, we are deprecating the Google Analytics (Universal Analytics) connector and recommend that you migrate to the [Google Analytics 4 (GA4) connector](https://docs.airbyte.com/integrations/sources/google-analytics-data-api) as soon as possible to ensure your syncs are not affected.

Due to this deprecation, we will not be accepting new contributions for this source, and OAuth is no longer supported as an authentication method for new connections in Airbyte Cloud.

For more information, see ["Universal Analytics is going away"](https://support.google.com/analytics/answer/11583528).

:::

## Prerequisite

* Administrator access to a Google Analytics 4 (GA4) property

## Setup guide

1. Click **Authenticate your account** by selecting Oauth (recommended).
   * If you select Service Account Key Authentication, follow the instructions in our [full documentation](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
2. Log in and Authorize the Google Analytics account.
3. Enter your [Property ID](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id)
4. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD.
5. (Optional) Airbyte generates 8 default reports. To add more reports, you need to add **Custom Reports** as a JSON array describing the custom reports you want to sync from Google Analytics. See below for more information.
6. (Optional) Enter the **Data request time increment in days**. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364.

## (Optional) Custom Reports
Custom Reports allow for flexibility in the reporting dimensions and metrics to meet your specific use case. Use the [GA4 Query Explorer](https://ga-dev-tools.google/ga4/query-explorer/) to help build your report. To ensure your dimensions and metrics are compatible, you can also refer to the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/).

A custom report is formatted as: `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}]`

Example of a custom report:
```
[{
  "name" : "page_views_and_users",    
  "dimensions" :[ 
    "ga:date",
    "ga:pagePath",      
    "ga:sessionDefaultChannelGrouping"
  ],
  "metrics" :[
    "ga:screenPageViews",
    "ga:totalUsers"
  ]
}]
```
Multiple custom reports should be entered with a comma separator. Each custom report is created as it's own stream. 
Example of multiple custom reports:
```
[
  {
    "name" : "page_views_and_users",    
    "dimensions" :[ 
      "ga:date",
      "ga:pagePath"
    ],
    "metrics" :[
      "ga:screenPageViews",
      "ga:totalUsers"
    ]
  },
  {
    "name" : "sessions_by_region",    
    "dimensions" :[ 
      "ga:date",
      "ga:region"
    ],
    "metrics" :[
      "ga:totalUsers",
      "ga:sessions"
    ]
  }
]
```

Custom reports can also include segments and filters to pull a subset of your data. The report should be formatted as: `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...], "segments":  ["<segment-id-or-dynamic-segment-name]", "filter": "<filter-name>"}]`

* When using segments, make sure you also add the `ga:segment` dimension.

Example of a custom report with segments and/or filters:
```
[{ "name" : "page_views_and_users",    
	"dimensions" :[ 
		"ga:date",
		"ga:pagePath",      
      "ga:segment"
   ],
   "metrics" :[
      "ga:sessions",
      "ga:totalUsers"
   ],
   "segments" :[
      "ga:sessionSource!=(direct)"
   ],
   "filter" :[
      "ga:sessionSource!=(direct);ga:sessionSource!=(not set)"
   ]
}]
```

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Analytics 4 (GA4)](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
