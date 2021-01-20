# Transformation and Schemas

### **Where's the T in Airbyte’s ETL tool?**

Airbyte is actually an ELT tool, and you have the freedom to use it as an EL-only tool. The transformation part is done by default, but it is optional. You can choose to receive the data in raw \(JSON file for instance\) in your destination. 

We do provide normalization \(if option is still on\) so that data analysts / scientists / any users of the data can use it without much effort. 

We also intend to integrate deeply with DBT to make it easier for your team to continue relying you on them, if this was what you were doing. 

### **How does Airbyte handle replication when a data source changes its schema?**

How Airbyte handles data structure changes in a data source varies depending on the connector, as well as the replication method used for a given table within that connector.

However, Airbyte decouples the Extract and Load of a source from the normalization of the data at the destination. So, the data will still land in your destination, but if you used any normalization, this part might be broken because of the schema change. 

At that point, you should see a failure displayed in Airbyte’s UI at the source level, along with all the detailed logs. You then have two options: 

* File a GitHub issue: go [here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=) and file an issue with the detailed logs copied in the issue’s description. The team will be notified about your issue and will update it for any progress or comment on it.  
* Fix the issue yourself: with open source, you don’t need to wait for anybody to fix your issue if it is important to you. In that case, just fork the [GitHub project](http://github.com/airbytehq/airbyte) and fix the connector you need fixed. If you’re okay with contributing your fix to the community, please then create a pull request. Don’t hesitate to ping the team on [Slack](https://slack.airbyte.io), so we can check your PR as soon as possible. But you do NOT need to wait for the PR to be approved to benefit from your own fix. Put your connector in a new folder, and add your connector directly through our UI by clicking on + New connector in the Admin section. This way, you will be able to use your connector as a separate one from the connector available to the community.

