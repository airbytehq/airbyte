# Salesforce

Airbyte destination connector for Salesforce Sales.

## Sync overview

Salesforce destination uses the Salesforce bulk API. It allows you to create and update Salesforce objects by batch upsert.

The API can access theses objects: 
- Account
- Case
- Contact
- Event
- Lead
- Oppportunity
- Profile
- User
- Task

## Getting start

- [Client ID](https://help.salesforce.com/s/articleView?id=sf.connected_app_rotate_consumer_details.htm&type=5)

- [Client Secret](https://help.salesforce.com/s/articleView?id=sf.connected_app_rotate_consumer_details.htm&type=5)

- [Refresh Token](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_refresh_token_flow.htm&type=5)

- Batch size: The number of records you want to push at the same time. Default: 10000

- Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account. 

- Salesforce Object: Select in the previous list which object you want to create/update. The default value is `Account`.


## Input Schema 

Salesforce API accepts only the fields that already exist in Salesforce platform, otherwise a problem will occur.

**The `Id` field is mandatory if you want to update records.
Otherwise, the API will create a new record.**




## CHANGELOG

| Version | Date       | Pull Request                                       | Subject                       |
| :------ | :--------- | :------------------------------------------------- | :---------------------------- |
| 0.1.0   | 2023-09-05 | [#3](https://github.com/sendinblue/airbyte/pull/3) | 🎉 New Destination: Salesforce |





