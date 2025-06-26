# ELT, data activation, and reverse-ETL

Airbyte supports two directions of data movement:

- "Traditional" extract, load, transform (ELT)
- "Reverse-ETL" or as Airbyte likes to call it, "data activation."

## Extract, load, transform

This work features movement from many databases and APIs into data warehouses and data lakes. This type of work is designed to power use cases like internal reporting, analytics, and more recently, AI.

## Data activation, aka reverse-extract, transform, load

Airbyte also works the other way: moving consolidated data out of data warehouses and back into the operational systems teams rely on. This effort is often called reverse-ETL or data activation. This process turns raw data into actionable, valuable insights by moving it to the higher-context systems where it can empower day-to-day work.

Imagine you want to give your sales team the maximum amount of context and knowledge possible. Your CRM, Salesforce, has a lot in it, but much of this information is manually entered by your sales reps based on customer calls and research.

You have a data warehouse filled with data you've synced from dozens or hundreds of other data sources.

You decide to make Salesforce more powerful by populating it with things like past customer behavior, how they engage with your marketing campaigns, past support experiences, etc. You sync this data automatically and regularly to keep it fresh based on the latest data in your sources.

This type of data gives your front-line customer-facing teams powerful insight about what their customers need, what they're struggling with, and what opportunities exist to improve customer satisfaction, land new accounts, and expand existing ones.
