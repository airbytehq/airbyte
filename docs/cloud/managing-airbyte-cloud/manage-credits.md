---
products: cloud
---

# Manage credits

Airbyte [credits](https://airbyte.com/pricing) are used to pay for Airbyte resources when you run a sync. 

Airbyte Cloud plans start at just $10 per month, with additional charges based on usage.

:::note
If you signed up for Airbyte Cloud on or after October 31st, 2024, you are automatically enrolled in our $10/month subscription plan.

For those who signed up prior, we will reach out to you over the coming weeks to migrate you to the new plans, and you can continue to use Airbyte as usual in the interim.
:::

## What are credits?

Airbyte uses credits to unify pricing across multiple types of sources. You can refer to the below table to understand how pricing differs across each source.

|Source Type| Billing Type| Price| Credit Equivalent|
|-|-|-|-|
|APIs | Rows| $15 per million rows| 6 credits|
|Databases| GB | $10 per GB| 4 credits|
|Files| GB | $10 per GB| 4 credits|
|Custom sources| Rows | $15 per million rows| 6 credits|

Airbyte Cloud plans start at $10 per month, which includes 4 credits. Additional credits are available at $2.50 each.

For APIs and custom sources, most syncs will sync incrementally, so the row amount will typically be those rows added, edited, or deleted. For Full Refresh syncs, every row synced will be charged. 

For Databases and File sources, Airbyte measures the data volume observed by the Airbyte Platform during the sync to determine data volumes. When the data is in transit, it is serialized to Airbyte Protocol format records. This is likely to be a larger representation of your data than you would see if you were to query your database directly, and varies depending on how your database stores and compresses data.

## Start a Trial
To begin a trial of Airbyte Cloud, head to https://cloud.airbyte.com/signup. Your trial will only begin after your first successful sync. Trials last 14 days or when 400 trial credits are used, whichever occurs first. 

## Add Payment Details
To continue using Airbyte beyond your trial, we require a valid payment method on file. We currently only accept credit card. If you prefer ACH, please [Talk to Sales](https://airbyte.com/company/talk-to-sales).

To add payment details, navigate to the Cloud UI.
1. Click on **Settings** in the navigation bar
2. Under **Organization**, click **Billing**
3. Enter **Payment Details**

Once your payment details have been saved, Airbyte will automatically charge the credit card on file  at the end of each month's billing period for usage incurred.

## View Billing Information
Once you have entered payment details, additional billing information will be shown. On the Organization Billing page, customers can see:
1. **Remaining credits**: The amount of credits that remain on the balance. The credits will be used first before we accrue an invoice amount.
2. **Upcoming Invoice Amount**: The amount of the upcoming invoice
3. **Invoice Date**: The date of the upcoming invoice

## Billing Notifications
Customers can enroll in billing notifications for their organization. The billing notifications available are:
- Notify me when a sync consumes over $__
- Notify me when my upcoming invoice has increased __%
- Notify me when my upcoming invoice is over $___

To enroll in billing notifications:
1. Click on **Settings** in the navigation bar
2. Under **Organization**, click **Billing**
3. Click on **Set up billing alerts**
4. Submit the form with custom thresholds for the alerts you are interested in receiving.

To change your existing notification thresholds, submit the form again.

To unenroll, [email us](mailto:billing@airbyte.io) with your request.

## Automatic reload of credits

You can enroll in automatic top-ups of your credit balance. 

To enroll, [email us](mailto:billing@airbyte.io) with:

1. A link to your workspace or organization that you'd like to enable this feature for.
2. **Recharge threshold** The number under what credit balance you would like the automatic top up to occur.
3. **Recharge balance** The amount of credits you would like to refill to.

As an example, if the recharge threshold is 10 credits and recharge balance is 30 credits, anytime your credit balance dips below 10 credits, Airbyte will automatically add enough credits to bring the balance back to 30 credits by charging the difference between your credit balance and 30 credits.

To take a real example, if:

1. The credit balance reached 3 credits.
2. 27 credits are automatically charged to the card on file and added to the balance.
3. The ending credit balance is 30 credits.

Note that the difference between the recharge credit amount and recharge threshold must be at least 20 as our minimum purchase is 20 credits.

If you are enrolled and want to change your limits or cancel your enrollment, [email us](mailto:billing@airbyte.io).