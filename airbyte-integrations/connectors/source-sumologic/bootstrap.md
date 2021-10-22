This connector uses sumologic python sdk https://github.com/SumoLogic/sumologic-python-sdk
The sdk is a wrapper of sumologic API https://help.sumologic.com/APIs
This connector implements the most common use case of sumologic: query and download. See seach job API details here: https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API

Future improvement ideas:
- The search job API supports auto parsing mode https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API#query-parameters, but it is not supported by their python sdk yet.
    One way to do it is to monkey patch the `search_job` method like:
    ```
    from sumologic import SumoLogic

    # Monkey patch SumoLogic to do auto parsing
    def search_job_patch(
        self,
        query,
        fromTime=None,
        toTime=None,
        timeZone='UTC',
        byReceiptTime=None,
        autoParsingMode='intelligent',
    ):
        params = {
            'query': query,
            'from': fromTime,
            'to': toTime,
            'timeZone': timeZone,
            'byReceiptTime': byReceiptTime,
            'autoParsingMode': autoParsingMode,
        }
        r = self.post('/search/jobs', params)
        return json.loads(r.text)

    SumoLogic.search_job = search_job_patch
    ```
    It is not implemented in the first version because it requires the output schema to be dynamic.
