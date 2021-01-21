# Transformation and Schemas

### **Where's the T in Airbyte’s ETL tool?**

Airbyte is actually an ELT tool, and you have the freedom to use it as an EL-only tool. The transformation part is done by default, but it is optional. You can choose to receive the data in raw \(JSON file for instance\) in your destination. 

We do provide normalization \(if option is still on\) so that data analysts / scientists / any users of the data can use it without much effort. 

We also intend to integrate deeply with DBT to make it easier for your team to continue relying you on them, if this was what you were doing. 

### **How does Airbyte handle replication when a data source changes its schema?**

Airbyte continues to sync data using the configured schema until that schema is updated. Because Airbyte treats all fields as optional, if a field is renamed or deleted in the source, that field simply will no longer be replicated, but all remaining fields will. The same is true for streams as well.

For now, the schema can only be updated manually in the UI (by clicking "Update Schema" in the settings page for the connection). When a schema is updated Airbyte will re-sync all data for that source using the new schema.


At that point, you should see a failure displayed in Airbyte’s UI at the source level, along with all the detailed logs. You then have two options: 

* File a GitHub issue: go [here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=) and file an issue with the detailed logs copied in the issue’s description. The team will be notified about your issue and will update it for any progress or comment on it.  
* Fix the issue yourself: with open source, you don’t need to wait for anybody to fix your issue if it is important to you. In that case, just fork the [GitHub project](http://github.com/airbytehq/airbyte) and fix the connector you need fixed. If you’re okay with contributing your fix to the community, please then create a pull request. Don’t hesitate to ping the team on [Slack](https://slack.airbyte.io), so we can check your PR as soon as possible. But you do NOT need to wait for the PR to be approved to benefit from your own fix. Put your connector in a new folder, and add your connector directly through our UI by clicking on + New connector in the Admin section. This way, you will be able to use your connector as a separate one from the connector available to the community.
