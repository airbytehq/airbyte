The (Robert Koch-Institut - von Marlon Lückert) Covid-19 is [a REST based API](https://api.corona-zahlen.org/). 
Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

## Cases In Germany Covid api stream
The basic entry stream is 'germany'. All other streams are extended version of base stream and passing parameters also result in sliced data.
For production, every developer application can view multiple streams. 

## Endpoints
* [Provides covid cases and other information in Germany.](https://api.corona-zahlen.org/germany) \(Non-Incremental\ Entry-Stream)
* [Provides covid cases and other information in Germany, group by age.](https://api.corona-zahlen.org/germany/age-groups) \(Non-Incremental\)
* [Provides cases in Germany based on days.](https://api.corona-zahlen.org/germany/germany/history/cases/:days) \(Incremental\)
* [Provides incidence rate of covid in Germany based on days.](https://api.corona-zahlen.org/germany/germany/history/incidence/:days) \(Incremental\)
* [Provides death rate in Germany over days](https://api.corona-zahlen.org/germany/germany/history/deaths/:days) \(Incremental\)
* [Provides recovery rate in Germany over days.](https://api.corona-zahlen.org/germany/germany/history/recovered/:days) \(Incremental\)
* [Provides frozen incidence in Germany over days.](https://api.corona-zahlen.org/germany/germany/history/frozen-incidence/:days) \(Incremental\)
* [Provides hospitalization rate in Germany over days.](https://api.corona-zahlen.org/germany/germany/history/hospitalization/:days) \(Incremental\)

## Cases In States Of Germany Covid api stream
The basic entry stream is 'GermanyStates'. All other streams are extended version of base stream and passing parameters also result in sliced data.
For production, every developer application can view multiple streams. 

## Endpoints
* [Provides covid cases and other information in Germany.](https://api.corona-zahlen.org/state) \(Non-Incremental\ Entry-Stream)
* [Provides covid cases and other information in Germany, group by age.](https://api.corona-zahlen.org/states/age-groupss) \(Non-Incremental\)
* [Provides cases in Germany based on days.](https://api.corona-zahlen.org/germany/states/history/cases/:days) \(Non-Incremental\)
* [Provides incidence rate of covid in Germany based on days.](https://api.corona-zahlen.org/germany/states/history/incidence/:days) \(Non-Incremental\)
* [Provides death rate in Germany over days](https://api.corona-zahlen.org/germany/states/history/deaths/:days) \(Non-Incremental\)
* [Provides recovery rate in Germany over days.](https://api.corona-zahlen.org/germany/states/history/recovered/:days) \(Non-Incremental\)
* [Provides frozen incidence in Germany over days.](https://api.corona-zahlen.org/germany/states/history/frozen-incidence/:days) \(Non-Incremental\)
* [Provides hospitalization rate in Germany over days.](https://api.corona-zahlen.org/germany/states/history/hospitalization/:days) \(Non-Incremental\)

Incremental streams have required parameter start-date. Without passing start-date as parameter full-refresh occurs.
As cursor field this connector uses "date". 