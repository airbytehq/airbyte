---
products: cloud
---

# Manage credits

Airbyte [credits](https://airbyte.com/pricing) are used to pay for Airbyte resources when you run a sync. Credits are purchased on Airbyte Cloud to keep your data flowing without interruption.

## What are credits?

Airbyte uses credits to unify pricing across multiple types of sources. You can refer to the below table to understand how pricing differs across each source.

|Source Type| Billing Type| Price| Credit Equivalent|
|-|-|-|-|
|APIs | Rows| $15 per million rows| 6 credits|
|Databases| GB | $10 per GB| 4 credits|
|Files| GB | $10 per GB| 4 credits|
|Custom sources| Rows | $15 per million rows| 6 credits|

The standard price for a credit is $2.50. 

For APIs and custom sources, most syncs will sync incrementally, so the row amount will typically be those rows added, edited, or deleted. For Full Refresh syncs, every row synced will be charged. 

For Databases and File sources, Airbyte measures the data volume observed by the Airbyte Platform during the sync to determine data volumes. When the data is in transit, it is serialized to Airbyte Protocol format records. This is likely to be a larger representation of your data than you would see if you were to query your database directly, and varies depending on how your database stores and compresses data.

## Buy credits
You can purchase credits anytime directly through your Airbyte workspace with a credit card. 

1. To purchase credits directly through the UI, click **Billing** in the left-hand sidebar. The billing page displays the available credits, total credit usage, and the credit usage per connection.

   :::tip

   If you are unsure of how many credits you need, use our [Cost Estimator](https://www.airbyte.com/pricing) or [Talk to Sales](https://airbyte.com/company/talk-to-sales) to find the right amount for your team.

   :::

2. Click **Buy credits**. Enter the quantity of credits you intend to purchase and adjust the **credit quantity** accordingly. When you're ready, click **Checkout**.

   :::note

   Purchase limits:

   - Minimum: 20 credits
   - Maximum: 6,000 credits

   :::

   To buy more credits or discuss a custom plan, reach out to [Sales](https://airbyte.com/talk-to-sales).

3. You'll be renavigated to a Stripe payment page. If this is your first time purchasing, you'll be asked for payment details. After you enter your billing address, sales tax (if applicable) is calculated and added to the total.

4. Click **Pay** to process your payment. A receipt for your purchase is automatically sent to your email.

   :::note

   Credits expire after one year if they are not used.

   :::

## Automatic reload of credits

You can enroll in automatic top-ups of your credit balance. This feature is for those who do not want to manually add credits each time.

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

## View invoice history

1. In the Airbyte UI, click **Billing** in the navigation bar.

2. Click **Invoice History**. You will be redirected to a Stripe portal.

3. Enter the email address used to make the purchase to see your invoice history. [Email us](mailto:ar@airbyte.io) for an invoice.
