There are several groups of streams:
- Stream may return data of services. Each such stream has the list of services which it supports.
If request tries to pull data of service which stream doesn't support this error will be covered and returned as a waring to user log.
If it's incremental, it uses [filtering](https://docs.railz.ai/reference/filtering) with gte/lte by cursor_field.
- Stream may have reports. Then it returns data are returned by report. Each one has it's meta with reportId, date range (and others)
and data field which may be a list or an object. If it's list then it returns each of it's elements as a record. Also each record contains fields from meta.
Request parameters may contain reportFrequency field which sets the range one of month/quarter/year. If there no such parameter, data will be returned by month.
Also for incremental it sets startDate and endDate.


Stream state for incremental services has an object which with structure below:
```
{
    [businessName]: {
        [serviceName]: {
            [cursor_field]: "{date string YYYY-MM-DD}" # in our case cursor_field will be start_time.
        }
    }
}
```
so each service of each business has own cursor_field and they will be incremented by it separately.
