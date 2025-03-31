---
products: cloud
---

# Manage credits

In order to manage your payment and billing information, you must be granted the **Organization Admin** role. 

## What are credits?

Airbyte [credits](https://airbyte.com/pricing) are used to pay for Airbyte resources when you run a sync. Airbyte Cloud plans start at $10 per month, which includes 4 credits. Additional credits are available at $2.50 each.

:::note
If you signed up for Airbyte Cloud on or after October 31st, 2024, you are automatically enrolled in our $10/month subscription plan.

For those who signed up prior, we will reach out to you over the coming weeks to migrate you to the new plans, and you can continue to use Airbyte as usual in the interim.
:::

Airbyte uses credits to unify pricing across multiple types of sources. You can refer to the below table to understand how pricing differs across each source.

|Source Type| Billing Type| Price| Credit Equivalent|
|-|-|-|-|
|APIs | Rows| $15 per million rows| 6 credits|
|Databases| GB | $10 per GB| 4 credits|
|Files| GB | $10 per GB| 4 credits|
|Custom sources| Rows | $15 per million rows| 6 credits|

For APIs and custom sources, most syncs will sync incrementally, so the row amount will typically be those rows added, edited, or deleted. For Full Refresh syncs, every row synced will be charged. 

For Databases and File sources, Airbyte measures the data volume observed by the Airbyte Platform during the sync to determine data volumes. When the data is in transit, it is serialized to Airbyte Protocol format records. This is likely to be a larger representation of your data than you would see if you were to query your database directly, and varies depending on how your database stores and compresses data.

## Start a Trial
To begin a trial of Airbyte Cloud, head to https://cloud.airbyte.com/signup. Your trial will only begin after your first successful sync. Trials last 14 days or when 400 trial credits are used, whichever occurs first. 

If you need additional trial credits or time to evaluate Airbyte, please reach out to our [Sales team](https://airbyte.com/company/talk-to-sales).

## Add Payment Details
To continue using Airbyte beyond your trial, we require a valid payment method on file. We currently only accept credit card. If you prefer ACH, please [Talk to Sales](https://airbyte.com/company/talk-to-sales).

To add payment details, navigate to the Cloud UI.
1. Click on **Settings** in the navigation bar
2. Under **Organization**, click **Billing**
3. Enter **Payment Details**

Once your payment details have been saved, Airbyte will automatically charge the credit card on file at the end of each month's billing period for the subscription amount and any additional usage incurred.

Once you have entered payment details, additional billing information will be shown:
- Plan
- Account Balance
- Billing Information
- Payment Method
- Invoice History

### Review Plan
The Plan section shows the Plan you are currently enrolled in. You may reach out to [Sales](https://airbyte.com/company/talk-to-sales) to inquire about Airbyte Teams features or custom discounts.

### Review Account Balance
In the Account Balance section, you can view: 
1. **Upcoming Invoice Amount**: The amount of the upcoming invoice
2. **Invoice Date**: The date of the upcoming invoice
3. **Remaining credits**: The amount of credits that remain on the balance. The credits will be used first before we accrue an invoice amount. This is typically only relevant if you pre-purchased credits before November 2024.

### Review Billing Information
In the Billing Information section, you can review:
1. The **Billing Email**, which we will use for any invoicing or billing notifications.
2. The **Billing Address**, which we will use to apply any applicable taxes to your invoice.

To edit the **Billing Email** or **Billing Address**, click **Update**. You will be redirected to the Stripe portal, where you can save any updates.

### Review Payment Method
In the Payment Method section, you can review the saved **Payment Method** on file. This will be used for any automatic monthly subscription or overage charges.

To edit the **Payment Method**, click **Update**. You will be redirected to the Stripe portal, where you can save any updates.

### Review Invoice History
In the Invoices section, you can review any past invoices. All invoices will note an **Invoice Status**. The **Invoice Status** indicates whether the invoice is still awaiting payment or are already paid.

You can view more details about an individal invoice by clicking **View Invoice**.

## Billing Notifications
By default, all customers will automatically review upcoming invoice notifications 3 and 7 days before the invoice will be finalized. All billing notifications will be sent to the **Billing Email** in the **Billing Information** section.

Customers can also optionally enroll in billing notifications for their organization. We highly recommend enrolling in billing notifications to ensure you stay up-to-date on your upcoming invoices. 

The billing notifications available are:
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

## Purchasing Credits

:::note
Credits can no longer be pre-purchased. As of November 2024, Airbyte Cloud has moved to in-arrears billing invoiced monthly.
:::

Purchased credits expire after 12 months after purchase. Purchased credits are used before accruing an invoice for additional usage. Purchased credits can not be used for the monthly subscription fee.