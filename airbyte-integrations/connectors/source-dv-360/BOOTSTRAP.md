# Display & Video 360

Google DoubleClick Bid Manager (DBM) is the API that enables developers to manage Queries and retrieve Reports from Display & Video 360.

DoubleClick Bid Manager API `v1.1` is the latest available and recommended version.

[Link](https://developers.google.com/bid-manager/v1.1) to the official documentation.

[Getting started with the API](https://developers.google.com/bid-manager/guides/getting-started-api) 

**Workflow of the API**:
* In order to fetch data from the DBM API, it is necessary to first build a [query](https://developers.google.com/bid-manager/v1.1/queries) that gets created in the [user interface (UI)](https://www.google.com/ddm/bidmanager/).
* Once the query is created it can be executed, and the resulting [report](https://developers.google.com/bid-manager/v1.1/reports) can be found and downloaded in the UI. 

**Filters and Metrics**: Dimensions are referred to as Filters in DV360. All available dimensions metrics can be found [here](https://developers.google.com/bid-manager/v1.1/filters-metrics).

**Note**: It is recommended in the reporting [best practices](https://developers.google.com/bid-manager/guides/scheduled-reports/best-practices) to first build the desired report in the UI to avoid any errors, since there are several limilations and requirements pertaining to reporting types, filters, dimensions, and metrics (such as valid combinations of metrics and dimensions).