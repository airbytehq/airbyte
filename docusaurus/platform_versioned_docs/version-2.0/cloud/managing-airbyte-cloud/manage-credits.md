---
products: cloud
---

# Manage billing and credits

In order to manage your payment and billing information, you need the **Organization Admin** role.

## What are credits?

Airbyte [credits](https://airbyte.com/pricing) are used to pay for Airbyte resources when you run a sync. Airbyte Cloud plans start at $10 per month, which includes 4 credits. Additional credits are available at $2.50 each.

Airbyte uses credits to unify pricing across multiple types of sources. You can refer to the below table to understand how pricing differs across each source.

| Source Type    | Billing Type | Price                | Credit Equivalent |
| -------------- | ------------ | -------------------- | ----------------- |
| APIs           | Rows         | $15 per million rows | 6 credits         |
| Databases      | GB           | $10 per GB           | 4 credits         |
| Files          | GB           | $10 per GB           | 4 credits         |
| Custom sources | Rows         | $15 per million rows | 6 credits         |

For APIs and custom sources, most syncs happen incrementally, so the row amount is typically those rows added, edited, or deleted. For Full Refresh syncs, every row synced is charged.

For Databases and File sources, Airbyte measures the data volume observed by the Airbyte Platform during the sync to determine data volumes. When the data is in transit, it is serialized to Airbyte Protocol format records. This is likely to be a larger representation of your data than you would see if you were to query your database directly, and varies depending on how your database stores and compresses data.

## Start a trial

To begin a trial of Airbyte Cloud, head to [cloud.airbyte.com/signup](https://cloud.airbyte.com/signup). Your trial begins after your first successful sync. Trials last 30 days or when you use 400 trial credits, whichever occurs first.

If you need additional trial credits or time to evaluate Airbyte, please reach out to Airbyte's [Sales team](https://airbyte.com/company/talk-to-sales).

## Access the Billing page

Follow these steps to access the Billing page.

1. Click **Organization settings** in the navigation bar.

2. Click **Billing**.

From this page, you can view and update your billing information.

## Add payment details

To continue using Airbyte beyond your trial, you must place a valid payment method on file. Airbyte currently only accepts credit cards. If you prefer ACH, [talk to Sales](https://airbyte.com/company/talk-to-sales).

To add payment details, click **Add payment method**.

Airbyte automatically charges the credit card on file at the end of each month's billing period for the subscription amount and any additional usage incurred. Once you enter payment details, Airbyte shows you additional billing information.

- Subscription
- Account balance
- Billing information
- Payment method
- Invoices

### Review your subscription

The Subscription section shows the subscription plan you have enrolled in. Reach out to [Sales](https://airbyte.com/company/talk-to-sales) to inquire about larger plans, new features, or custom discounts.

### Review your account balance

In the Account balance section, you can view more details about your balance.

- **Upcoming invoice amount**: The amount of the upcoming invoice

- **Invoice date**: The date of the upcoming invoice

- **Remaining credits**: The amount of credits that remain. Airbyte uses these credits first before it accrues an invoice amount. This is typically only relevant if you pre-purchased credits before November 2024.

### Review billing information

In the Billing information section, you can review:

- Your **billing email**, which Airbyte uses for invoicing and billing notifications.

- Your **billing address**, which Airbyte uses to apply any applicable taxes to your invoice.

To edit your billing email or address, click **Update**. Airbyte redirects to the Stripe portal, where you can save any updates.

### Review payment method

In the Payment method section, you can review the saved credit card on file. Airbyte uses this for any automatic monthly subscription or overage charges.

To edit the **Payment Method**, click **Update**. Airbyte redirects to the Stripe portal, where you can save any updates.

### Review invoice history

In the Invoices section, you can review any past invoices. All invoices have an **Invoice status**. The invoice status indicates whether the invoice is still awaiting payment or are already paid.

You can view more details about an individual invoice by clicking **View Invoice**.

## Billing notifications

By default, all customers automatically review upcoming invoice notifications 3 and 7 days before the invoice is finalized. All billing notifications are sent to the billing email on file.

You can also enroll in billing notifications for your organization. Airbyte highly recommends enrolling in billing notifications to ensure you stay up-to-date on your upcoming invoices.

Airbyte can notify you when:

- A sync consumes over $__

- Your upcoming invoice has increased __%

- Notify me when my upcoming invoice is over $___

To enroll in or modify your existing billing notifications:

1. From the Billing page, click **Set up billing alerts**.

2. Submit the form with the thresholds you want to use for alerts.

To unenroll, [email the Billing team](mailto:billing@airbyte.io) with your request.

## Purchasing credits

You can no longer pre-purchase credits. As of November 2024, Airbyte Cloud has moved to in-arrears billing. You're invoiced monthly.
