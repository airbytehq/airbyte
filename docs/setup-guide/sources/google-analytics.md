# Google Analytics 4 (GA4)

This page contains the setup guide and reference information for Google Analytics 4 (GA4).

## Prerequisites

* A Google Analytics account with access to the GA4 property you want to sync
* Google Service Account JSON Key
* Google Analytics Property ID

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Create a GA4 Service Account for authentication

1. Sign in to the Google Account you are using for GA as an admin.

2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page in the Google Developers console.
![GA4 Service Accounts](/docs/setup-guide/assets/images/ga4-service-accounts.jpg "GA4 Service Accounts")

3. Select the project you want to use (or create a new one).

4. Click **+ Create Service Account** at the top of the page.
![GA4 Create Service Account](/docs/setup-guide/assets/images/ga4-create-service-account.jpg "GA4 Create Service Account")

5. Enter a name for the service account, and click **Create and Continue**.
![GA4 Service Account Details](/docs/setup-guide/assets/images/ga4-service-account-details.jpg "GA4 Service Account Details")

6. Choose the role for the service account. We recommend the **Viewer role (Read & Analyze permissions)**. Click Continue. And then click Done.
![GA4 Service Account Role](/docs/setup-guide/assets/images/ga4-service-account-role.jpg "GA4 Service Account Role")

7. Select your new service account from the list, and open the Keys tab. Click **Keys** > **Add Key**.
![GA4 Service Account Add Key](/docs/setup-guide/assets/images/ga4-service-account-add-key.jpg "GA4 Service Account Add Key")

8. Select **JSON** as the Key type. Then click Create. This will generate and download the JSON key file that you'll use for authentication.

### Step 2: Enable the Google Analytics APIs

1. Go to the [Google Analytics Reporting API dashboard](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview). Make sure you have selected the associated project for your service account, and **Enable** the API. You can also set quotas and check usage.
![GA4 Reporting API](/docs/setup-guide/assets/images/ga4-reporting-api.jpg "GA4 Reporting API")

2. Go to the [Google Analytics API dashboard](https://console.cloud.google.com/apis/api/analytics.googleapis.com/overview). Make sure you have selected the associated project for your service account, and **Enable** the API.
![GA4 API](/docs/setup-guide/assets/images/ga4-api.jpg "GA4 API")

3. Go to the [Google Analytics Data API dashboard](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com). Make sure you have selected the associated project for your service account, and Enable the API.
![GA4 Data API](/docs/setup-guide/assets/images/ga4-data-api.jpg "GA4 Data API")

### Step 3: Obtain your GA4 property id

1. Sign in to the [Google Analytics account](https://analytics.google.com/) as an admin.

2. On the left sidebar, click **Admin**.
![GA4 Admin](/docs/setup-guide/assets/images/ga4-admin.jpg "GA4 Admin")

3. Click **Property**.
![GA4 Property](../docs/setup-guide/assets/images/ga4-property.jpg "GA4 Property")

4. Click **Property details** and you will find your **Property ID** on the top right corner. This ID should be a numeric value, such as `123456789`. Copy it for later use.
![GA4 Property ID](/docs/setup-guide/assets/images/ga4-property-id.jpg "GA4 Property ID")

### Step 4: Grant Service Account GA4 property access

1. Following Step 3, inside the **Admin** area of your GA4 account, click **Account Access Management**.
![GA4 Account Access](/docs/setup-guide/assets/images/ga4-account-access.jpg "GA4 Account Access")

2. Click the blue **+** button in the right top corner of your screen. And click **Add Users**.
![GA4 Add User](/docs/setup-guide/assets/images/ga4-add-user.jpg "GA4 Add User")

3. Enter the email address of your Service Account user you created in Step 1. You can find the email listed in [Service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) in your Google Cloud Platform.
![GA4 Service Account Email](/docs/setup-guide/assets/images/ga4-service-account-email.jpg "GA4 Service Account Email")

4. Assign a role to the Service Account user. Daspire only needs the **Viewer** role. And click **Add**.
![GA4 Roles](/docs/setup-guide/assets/images/ga4-roles.jpg "GA4 Roles")

### Step 5: Set up GA4 in Daspire

1. Select **Google Analytics 4 (GA4)** from the Source list.

2. Enter a **Source Name**.

3. Select **Service Account Key Authenication** dropdown list and enter **Service Account JSON Key** you obtained from Step 1.

4. Enter the **GA4 Property ID** you obtained from Step 3.

5. (Optional) In the **Start Date** field, enter a date in the format `YYYY-MM-DD`. All data added from this date onward will be replicated. Note that this setting is not applied to custom Cohort reports.

  > Note: If the start date is not provided, the default value will be used, which is two years from the initial sync.

6. (Optional) In the **Custom Reports** field, you may optionally provide a JSON array describing any custom reports you want to sync from GA4. See the Custom Reports section below for more information on formulating these reports.

7. (Optional) In the **Data Request Interval (Days)** field, you can specify the interval in days (ranging from 1 to 364) used when requesting data from the Google Analytics API. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. This field does not apply to custom Cohort reports. See the Data Sampling section below for more context on this field.

8. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [daily_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [devices](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [four_weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [locations](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [pages](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_sources](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [website_overview](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [weekly_active_users](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_medium_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_source_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_source_medium_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_source_platform_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_campaign_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_google_ads_ad_network_type_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [user_acquisition_first_user_google_ads_ad_group_name_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_source_medium_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_medium_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_source_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_campaign_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_default_channel_grouping_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [traffic_acquisition_session_source_platform_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [events_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [weekly_events_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [conversions_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [pages_title_and_screen_class_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [pages_path_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [pages_title_and_screen_name_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [content_group_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_name_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_id_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_report_combined](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_2_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_3_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_4_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_category_5_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [ecommerce_purchases_item_brand_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [publisher_ads_ad_unit_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [publisher_ads_page_path_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [publisher_ads_ad_format_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [publisher_ads_ad_source_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_country_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_region_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_city_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_language_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_age_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_gender_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [demographic_interest_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_browser_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_device_category_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_device_model_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_screen_resolution_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_app_version_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_platform_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_platform_device_category_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_operating_system_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [tech_os_with_version_report](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
* [Custom stream(s)](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)

## Integration-specific features

### Custom Reports

Custom reports in GA4 allow for flexibility in querying specific data tailored to your needs. You can define the following components:

* **Name:** The name of the custom report.
* **Dimensions:** An array of categories for data, such as city, user type, etc.
* **Metrics:** An array of quantitative measurements, such as active users, page views, etc.
* **CohortSpec:** (Optional) An object containing specific cohort analysis settings, such as cohort size and date range. More information on this object can be found in the [GA4 documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/CohortSpec).
* **Pivots:** (Optional) An array of pivot tables for data, such as page views by city, etc. More information on pivots can be found in the [GA4 documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot).

A full list of dimensions and metrics supported in the API can be found [here](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema). To ensure your dimensions and metrics are compatible for your GA4 property, you can use the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/).

Custom reports should be constructed as an array of JSON objects in the following format:
```
[
  {
    "name": "<report-name>",
    "dimensions": ["<dimension-name>", ...],
    "metrics": ["<metric-name>", ...],
    "cohortSpec": {/* cohortSpec object */},
    "pivots": [{/* pivot object */}, ...]
  }
]
```

The following is an example of a basic User Engagement report to track sessions and bounce rate, segmented by city:
```
[
  {
    "name": "User Engagement Report",
    "dimensions": ["city"],
    "metrics": ["sessions", "bounceRate"]
  }
]
```

By specifying a cohort with a 7-day range and pivoting on the city dimension, the report can be further tailored to offer a detailed view of engagement trends within the top 50 cities for the specified date range.
```
[
  {
    "name": "User Engagement Report",
    "dimensions": ["city"],
    "metrics": ["sessions", "bounceRate"],
    "cohortSpec": {
      "cohorts": [
        {
          "name": "Last 7 Days",
          "dateRange": {
            "startDate": "2023-07-27",
            "endDate": "2023-08-03"
          }
        }
      ],
      "cohortReportSettings": {
        "accumulate": true
      }
    },
    "pivots": [
      {
        "fieldNames": ["city"],
        "limit": 50,
        "metricAggregations": ["TOTAL"]
      }
    ]
  }
]
```

### Data Sampling and Data Request Intervals

Data sampling in GA4 refers to the process of estimating analytics data when the amount of data in an account exceeds Google's predefined compute thresholds. To mitigate the chances of data sampling being applied to the results, the Data Request Interval field allows users to specify the interval used when requesting data from the Google Analytics API.

By setting the interval to 1 day, users can reduce the data processed per request, minimizing the likelihood of data sampling and ensuring more accurate results. While larger time intervals (up to 364 days) can speed up the sync, we recommend choosing a smaller value to prioritize data accuracy unless there is a specific need for faster synchronization at the expense of some potential inaccuracies. Please note that this field does not apply to custom Cohort reports.

Refer to the [Google Analytics documentation](https://support.google.com/analytics/topic/13384306?sjid=2450288706152247916-NA) for more information on data sampling.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Troubleshooting

1. The Google Analytics integration is subject to Google Analytics Data API quotas. Please refer to [Google's documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas) for specific breakdowns on these quotas.

2. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
