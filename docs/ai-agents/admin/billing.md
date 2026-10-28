---
plan: all
---

# Billing and pricing

Airbyte Agents bills you based on a unit of measurement called [agent operations (AOs)](../concepts/agent-operations.md). All plans come with a specific number of free AOs, and most plans allow you to exceed this limit for an additional cost. Your plan determines:

- How many free AOs you have each month.
- Whether you can exceed that limit and how much overage costs.
- How often Airbyte refreshes data in your Context Store.

## Manage payments

Manage payment methods and billing information from the Billing page.

### Add a payment method

If you don't have a payment method on file, the Payment Method card shows **No payment method on file**.

1. On the Billing page, in the Payment Method card, click **Add payment method**.
2. Enter your card details and billing address.
3. Click **Save**.

Adding a payment method is a prerequisite for upgrading to the Individual plan. Team and Custom plans are sales-assisted, and Airbyte configures billing as part of your contract.

### Update your payment method

To replace the card on file:

1. On the Billing page, in the Payment Method card, click **Update**.
2. Enter the new card details.
3. Click **Save**.

### Update your billing information

Your billing information is the email address and mailing address Airbyte uses on invoices and receipts.

1. On the Billing page, in the Billing Information card, click **Update**.
2. Update the contact email or address.
3. Click **Save**.

## Monitor usage

The Usage panel on the Billing page shows how your activity consumes AOs and tool calls over time. Chat usage includes AOs from tool calls and reasoning. MCP, API, SDK, and CLI usage includes AOs from tool calls only.

### View usage

The Usage panel displays a stacked bar chart of included AOs and overage AOs over the selected time range. Click a legend item to hide or show that series. Hover over a bar to see the AO breakdown for that day.

### Filter usage

Filter the Usage panel to focus on a specific source or time range:

- **Source**: Filter by where the activity originated. Sources include Chat, MCP, API, SDK, and CLI.
- **Billing period**: Choose the current billing period or one of the last five billing periods.
- **Custom range**: Pick any start and end date to view usage across an arbitrary window.

To investigate the tool calls and reasoning that drove a particular spike, use the [Sessions](./sessions.md) and [Tool calls](./tool-calls.md) pages.

### Understand included and overage AOs

Airbyte splits your usage into two buckets:

- **Included AOs**: AOs that fit within your monthly included allowance.
- **Overage AOs**: AOs that exceed your monthly allowance, billed at your plan's overage rate.

The Usage panel summary shows the totals for both. The Free plan can't exceed its monthly allowance, so it never accrues overage AOs.

## Invoices

Airbyte bills the payment method on file once per month. Find past invoices on the Billing page in the Invoices panel.

Each row shows the invoice date, amount, status, and actions.

- **Paid**: Airbyte successfully charged your payment method.
- **Not Paid**: Airbyte couldn't charge your payment method, or the invoice isn't paid yet.

### Pay an invoice

If an invoice is Not Paid, the Payment Method card displays a banner that tells you how many unpaid invoices you have and their total amount.

To pay an unpaid invoice:

1. On the Billing page, find the invoice in the Invoices panel.
2. Click **Pay now**.
3. Confirm the payment method and complete the charge.

If you can't pay with the card on file, [update your payment method](#update-your-payment-method) first, then retry.

### Download an invoice

In the Invoices panel, click the download icon next to an invoice to save a copy.

### Automatic invoice at $10,000 {#auto-bill}

If your charges for a billing period reach $10,000, Airbyte automatically issues an invoice and bills the payment method on file. This is in addition to your regular monthly invoice. After the automatic invoice, charges continue to accrue normally for the rest of the billing period.

## Avoid billing surprises

To avoid unexpected charges, monitor the [Usage panel](#monitor-usage) regularly and review your invoices as they arrive. If your charges reach $10,000 in a billing period, Airbyte [automatically generates an invoice and bills you](#auto-bill).

## Cancel your subscription

You can cancel a paid subscription from the Billing page. When you cancel:

- Active syncs stop running.
- Airbyte permanently deletes cached data in the Context Store.
- Airbyte removes your connector configurations.
- Airbyte revokes your API keys.
- Human support access ends.

Your subscription stays active until the end of your current billing period, and Airbyte won't charge you for the following period.

To cancel:

1. On the Billing page, in the Subscription card, click **Change your plan**.
2. Select the Free plan, or contact Airbyte to cancel a Custom plan.
3. Review what you'll lose access to, and confirm the cancellation.

## Plans

Airbyte Agents offers four plans. Free and Individual are self-serve. You can upgrade to them directly from the Billing page. Team and Custom plans are sales-assisted. Contact [Airbyte Sales](https://airbyte.com/company/talk-to-sales) to sign up for these plans.

### Free

A plan to explore Airbyte Agents and prototype agents.

- $0 per month.
- 1,000 AOs per month.
- Overage isn't available. When you reach your monthly limit, agent operations pause until the next billing period.
- Context Store refreshes hourly during your first 2 weeks, then daily.
- AI and community support.

### Individual

A plan for personal use and daily work.

- $29 per month.
- 5,000 AOs per month.
- Overage AOs are available.
- Context Store refreshes hourly.
- Standard human support, in addition to AI and community support.

You must [add a payment method](#add-a-payment-method) before you upgrade to the Individual plan.

### Team

A plan for teams with higher usage needs.

- $299 per month.
- 10,000 AOs per month.
- Overage AOs are available.
- Context Store refreshes hourly.
- [Multiple workspaces](../concepts/architecture/workspaces.md).
- [Single sign-on and SAML](./sso.md).
- [Multiple users](./users.md).
- Standard human support, in addition to AI and community support.

### Custom

A plan for large companies and embedded products. Airbyte tailors pricing, usage limits, and feature access to your needs. Custom plans include:

- An authentication module for embedding connector authentication in your app.
- A dedicated account manager.
- Service level agreements.
- Dedicated human support.
- Everything included in the Team plan.
