## Prerequisites

* BambooHR [API Key](https://documentation.bamboohr.com/docs#authentication)


## Setup guide
1. Name your BambooHR connector
2. Enter your `api_key`. To generate an API key, log in and click your name in the upper right-hand corner of any page to get to the user context menu. If you have sufficient administrator permissions, there will be an "API Keys" option in that menu to go to the page.
3. Enter your `subdomain`. If you access BambooHR at https://mycompany.bamboohr.com, then the subdomain is "mycompany"
4. (Optional) Enter any `Custom Report Fields` as a comma-separated list of fields to include in your custom reports. Example: `firstName,lastName`. If none are listed, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned.
5. Toggle `Custom Reports Include Default Fields`. If true, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned. If false, then the values defined in `Custom Report Fields` will be returned. 
6. Click **Set up source**

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [BambooHR](https://docs.airbyte.com/integrations/sources/bamboo-hr).
