# Abalustre Airbyte's connectors

This document list all Abalustre Airbyte's connectors and how to install them.

## Install Airbyte's connector

1 - Login in Airbyte

2 - Navigate to Settings on the sidebar

3 - Navigate to Sources in the internal menu

4 - Click on the button `+ New Connector` on the top right

5 - Fill in the formulary fields

[Here](https://docs.airbyte.io/integrations/custom-connectors#adding-your-connectors-in-the-ui) is the Airbyte's documentation to install connectors.


## Abalustre connectors

### HTTP Request

This connector makes HTTP requests allowing the user to configure dates and dates period as variables.

**Path**: airbyte/airbyte-integrations/connectors/source-http-request

**Docker image**: Execute inside the connector path the command:
```bash
docker build . -t airbyte/source-http-request:0.1.0
```

**New connector form**

****
**Connector display name**: HTTP Request

**Docker repository name**: airbyte/source-http-request

**Docker image tag**: 0.1.0

**Connector Documentation URL**: None

#### How to use it?

The HTTP Request connector has the following fields:

**url**: The URL that will be requested

**http_method**: The HTTP method which can be GET or POST

**headers**: The header for the HTTP Request

**body**: The body for the HTTP Request if the method is POST

**params**: The params are the variables that will be replaced in the URL for the HTTP Request

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The params can be a date or a period. It is an array of JSON data with the information:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Date JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `date`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "date", "unit": "month", "format": "%Y%m", "variable": "month_year", "value":  "current"}]
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Period JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `period`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**start_date**: It is the JSON with the first date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**end_date**: It is the JSON with the second date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "period", "unit": "day", "format": "%m-%d-%Y", "start_date": {"variable": "from", "value": "current - 1"}, "end_date": {"variable": "to", "value": "current + 1"}}]
```

**response_format**: It is the response format that can be `csv` or `json`

**response_delimiter**: It is the response delimiter when the format is `csv`



##### Example Date:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{month_year}.csv

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: GET

&nbsp;&nbsp;&nbsp;&nbsp;**params**: [{"type": "date", "unit": "month", "format": "%Y%m", "variable": "month_year", "value": "current"}]

&nbsp;&nbsp;&nbsp;&nbsp;**response_format**: csv

&nbsp;&nbsp;&nbsp;&nbsp;**response_delimiter**: ;



##### Example Period:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='AUD'&@dataInicial='{from}'&@dataFinalCotacao='{to}'&$format=json

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: GET

&nbsp;&nbsp;&nbsp;&nbsp;**params**: [{"type": "period", "unit": "day", "format": "%m-%d-%Y", "start_date": {"variable": "from", "value": "current - 1"}, "end_date": {"variable": "to", "value": "current + 1"}}]

&nbsp;&nbsp;&nbsp;&nbsp;**response_format**: json
