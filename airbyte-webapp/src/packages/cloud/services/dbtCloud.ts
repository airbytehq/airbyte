// This module is for the business logic of working with dbt Cloud webhooks.
// Static config data, urls, functions which wrangle the APIs to manipulate
// records in ways suited to the UI user workflows--all the implementation
// details of working with dbtCloud jobs as webhook operations, all goes here.
// The presentation logic and orchestration in the UI all goes elsewhere.

export const webhookConfigName = "dbt cloud";
export const executionBody = `{"cause": "airbyte"}`;
