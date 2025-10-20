---
products: all
---

# CDC best practices

This guide provides best practices for configuring and using Change Data Capture (CDC) with Airbyte. While configuration
explanations are included in the docs for each connector, this guide focuses on how to optimize these settings based on your data
size, activity patterns, and sync requirements.

:::note
This guide assumes basic familiarity with CDC concepts. For an introduction to how CDC works in Airbyte, see
[CDC documentation](./cdc).
:::

## Source configuration

<details>
<summary><strong>Initial Waiting Time </strong></summary>

**What it does:**

- **During the snapshot phase:** Sets the time limit for building the schema structure and capturing baseline data
- **During CDC incremental:** Determines how long Airbyte waits for new change events, helping to capture delayed changes before timing out

**Configuration range:** varies by source (check your source configuration page).

**Best practices:**

| Scenario | Recommendation                                | Reasoning |
|----------|-----------------------------------------------|-----------|
| Default use case | Start with the default value                  | Adjust only if experiencing timeouts |
| High-activity databases | Keep default                                  | Changes arrive frequently, shorter waits are sufficient |
| Low-activity databases | Increase by 300 s minimum                     | Longer waits help capture infrequent changes |
| Many schemas/tables | Increase value during snapshot and CDC phases | Gives Debezium more time to process changes across schemas |
| Simple schemas | Default values work well                      | No adjustment needed |

:::tip
For high-activity databases with many schemas/tables, you may still need to increase this value despite frequent changes
. Schema complexity affects processing time independently of data volume.
:::

</details>

<details>
<summary><strong>Invalid CDC Position Behavior </strong></summary>

**What it does:**

Determines how Airbyte responds when the CDC position becomes invalid (typically due to WAL recycling or extended gaps
between syncs).

**Available options:**

| Method       | Re-sync Data (Automatic Recovery)                                                                                                          | Fail Sync (Manual Intervention)                                                                           |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Behavior** | Automatically triggers a full refresh, re-snapshotting the entire database when CDC position is lost.                                      | Stops the sync and marks it as failed. No automatic action is taken.                                      |
| **Pros**     | • Fully automated<br/>• Ensures data consistency                                                                                           | • Allows investigation and controlled resolution<br/>• Prevents unexpected resource consumption and costs |
| **Cons**     | • Time-consuming for large datasets<br/>• Resource-intensive<br/>• Can lead to unexpected costs (compute, database load, writes, transfer) | • Requires manual restart after resolving the issue<br/>• Potential data gaps until resolved              |
| **Best for** | Small datasets, development environments                                                                                                   | Production environments, large databases                                                                  |

**Recommended approach:**

| Environment | Recommendation | Rationale |
|-------------|----------------|-----------|
| Production | Fail Sync | Better error handling, prevents surprise costs |
| Large databases | Fail Sync | Avoids expensive automatic re-snapshots |
| Development | Either option | Lower stakes, both approaches work |
| Small datasets | Either option | Re-sync is quick and inexpensive |

</details>

<details>
<summary><strong> Queue Size </strong></summary>

**What it does:**

Controls the internal buffer size for change events. Determines how many CDC records can be queued in memory before processing.

**Impact:**

- **Larger queue:** Handles burst changes efficiently but uses more memory
- **Smaller queue:** Lower memory usage, but may reduce sync efficiency

**Best practice:**

:::danger Critical
Keep this at the default value (10,000). Improper sizing impacts memory consumption, sync efficiency, and
system stability. Only modify this parameter if you have a specific technical reason or have been instructed to do so
by Airbyte support.
:::

</details>

<details>
<summary><strong>Initial Load Timeout </strong></summary>

**What it does:**

Sets the maximum duration for the snapshot phase. Once this time limit is reached or the snapshot completes (whichever
comes first), Airbyte captures the current LSN and switches to CDC streaming mode. **The maximum allowed value is 24
hours.**

**Best practices:**

| Database Size                  | Recommended Timeout | Notes |
|--------------------------------|---------------------|-------|
| Small to medium                | 8 hours (default) | Sufficient for most databases |
| Large databases                | 12-24 hours | Allows a complete snapshot before CDC streaming |
| Very large databases (> 50 GB) | 24 hours | Adjust based on observed snapshot duration |

:::tip
Monitor your first sync's snapshot duration to determine if you need to adjust this value.
:::

</details>

## General Airbyte configuration

<details>
<summary><strong> Sync Frequency </strong></summary>

Choose sync frequency based on your use case, data velocity, and WAL retention period.

**Key considerations:**

- **Sync frequency must be shorter than WAL retention period**
  - If retention is 3 days, sync at least every 2 days
  - Prevents LSN loss and sync failures
- **Balance data volume and sync overhead**
  - Avoid accumulating millions of records between syncs
  - Minimize empty syncs (no changes to capture)
  - Find the middle ground for your change volume
- **Near real-time requirements**
  - High-velocity data: Sync multiple times per day
  - Standard updates: Daily syncs often sufficient
  - Low activity: Match sync frequency to change patterns

**Recommended configurations:**

| Use Case | Sync Frequency | Retention Period | Notes |
|----------|----------------|------------------|-------|
| Near real-time replication | Every 1-4 hours | 7 days (recommended), 3 days minimum if data is highly active | Only sync this frequently if you have active data changes to avoid empty syncs |
| Daily business reporting | Once daily | 7 days (recommended), 3 days minimum if data is highly active | Standard configuration for most use cases |
| Weekly analytics | 2-3 times per week | 7 days minimum | Longer retention required for less frequent syncs |

:::tip
While 7-day retention is recommended for all scenarios, you may use shorter retention periods (3+ days) if your database
is highly active and you're confident your sync frequency will remain consistent. However, 7 days provides the best
buffer against unexpected delays or maintenance windows.
:::
</details>

## Database-level CDC configuration

<details>
<summary><strong> WAL Retention Period </strong></summary>

The WAL retention period determines how long transaction logs are stored before recycling. This is configured in your
database, not in Airbyte.

**Recommended configuration:**

| Priority | Retention Period | Rationale |
|----------|------------------|-----------|
| Optimal | 7 days | Covers weekend maintenance, most data movement scenarios |
| Minimum | Longer than sync frequency | Prevents LSN loss between syncs |

**Example scenarios:**

- **Syncing every 6 hours:** Minimum 1-2 days retention (7 days recommended)
- **Syncing daily:** Minimum 2-3 days retention (7 days recommended)
- **Syncing every 3 days:** Minimum 4-5 days retention (7 days recommended)

:::info Important
While Airbyte syncs can operate efficiently with short retention periods (when paired with appropriate sync frequency),
7-day retention provides the best buffer against unexpected delays or maintenance windows.
:::

</details>
