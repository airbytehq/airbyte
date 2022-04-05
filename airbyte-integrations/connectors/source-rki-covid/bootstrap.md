The (Robert Koch-Institut - von Marlon Lückert) Covid-19 is [a REST based API](https://api.corona-zahlen.org/). 
Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

## Cases In Germany Covid api stream
The basic entry stream is 'germany'. All other streams are extended version of base stream and passing parameters also result in sliced data.
For production, every developer application can view multiple streams. 
[This endpoint](https://api.corona-zahlen.org/germany/germany/history/cases/:days) gets a list of cases in germany in perticular day.

## Other streams
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/cases/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/incidence/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/deaths/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/recovered/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/frozen-incidence/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/germany/history/hospitalization/1) \(Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany) \(Non-Incremental\)
* [This endpoint](https://api.corona-zahlen.org/germany/age-groups) \(Non-Incremental\)



Incremental streams have required parameter days. Without passing days as parameter full-refresh happens.
As cursor field this connector uses "date". 