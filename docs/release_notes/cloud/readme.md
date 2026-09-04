# Airbyte Cloud release notes

Airbyte Cloud is updated continuously. You always have the latest features and fixes.

## September 4, 2026

Platform

- On Cloud Pro and Enterprise Flex plans, the Audit Logs page in Organization settings now shows a loading indicator while it fetches results after you change a filter or move to another page. Previously, the earlier results stayed on screen with no sign that a new request was in progress.

## September 1, 2026

Connections

- When you authenticate the Salesforce source or the HubSpot destination with OAuth, the consent step now completes. Airbyte previously formatted part of the authorization request in a way these providers reject, which could cause the authorization to fail.

Platform

- On Cloud Pro and Enterprise Flex plans, the data worker usage chart in your organization's Usage settings has a new Compare to previous period option. Turning it on shows the selected period next to the equivalent previous day, week, month, quarter, or year, so you can see whether your peak capacity usage is trending up or down.
- The Billing page now shows the date your next invoice is scheduled to be issued. You see the same date in the confirmation messages when you cancel your subscription or delete a workspace.

## August 31, 2026

Platform

- If your organization is on a capacity-based plan, the Usage page in Organization settings now offers 1Q and 1Y date ranges alongside 1D, 1W, and 1M, so you can review data worker usage across a full quarter or year.
- The Plus and Pro cards on the Plan page in Organization settings now list the support coverage each plan includes. Hover over the info icon next to a support line to see the exact hours and response times.

## August 27, 2026

Platform

- If your organization is on a capacity-based plan (Pro or Enterprise Flex), the workspace Usage page now shows which region the workspace runs in, alongside its data worker usage. This makes it easier to tell which region's capacity your workspace consumes.
- If your organization signs in with single sign-on but your plan doesn't include role-based access control, people who sign in for the first time are now added as organization admins. Previously they could be left with a role that nobody in your organization was able to change.
- If your organization is on the Plus plan, reported usage no longer schedules an unintended downgrade to the Standard plan. Your plan stays as you purchased it.

## August 26, 2026

Platform

- If your organization has committed data worker capacity, you can now switch the data worker usage graphs between one-day, one-week, and one-month ranges instead of always seeing a fixed window.

API

- You can now choose the time zone for a cron sync schedule when you create or update a connection through the API, so your syncs run at the hour you expect in your own time zone rather than always in UTC. Error messages for invalid cron schedules also explain the requirements more clearly.

## August 25, 2026

Connections

- When schema changes are applied to your connection, the affected incremental streams are now backfilled correctly so your destination data stays complete and accurate.
- When you create a new private link for S3 storage, the DNS name Airbyte gives you is now correct. Previously, the provided hostname could cause connection checks to fail with a certificate error. Existing private links are not changed.

Platform

- The Data Worker usage chart on the workspace usage page now shows hourly usage as bars, matching the look of the organization usage chart, so it's easier to compare usage across the two views.

## August 24, 2026

Platform

- If you're an organization admin on the Enterprise Flex plan, you can now view audit logs directly in Airbyte. The new Audit Logs page in your organization settings shows who changed what and when across your organization, with filters for date range, workspace, actor, and operation. Click any entry to see the full details of that event and copy them to your clipboard.

## August 21, 2026

Platform

- The Data Worker usage chart on your organization's Usage page is easier to read. Each day now has a single bar for peak usage instead of stacked, color-coded workspace segments, and hovering over a bar shows your region's peak next to a per-workspace breakdown. The dates along the bottom of the chart also display correctly now. This chart is available if your plan includes contracted Data Worker capacity.

## August 20, 2026

Connections

- When Airbyte provides its own OAuth application for a connector, the source and destination setup forms no longer show the manual authentication option. This prevents confusion by hiding fields that asked for developer credentials you don't need.

Platform

- If your organization manages users through your identity provider with SCIM, workspace settings now show a SCIM badge and no longer allow you to add or change workspace members directly in Airbyte. This keeps your membership consistent with your identity provider.
- If you store audit logs in your own bucket on the Enterprise Flex plan, Airbyte now organizes those log files into folders by organization and date, making them easier to browse and manage.

## August 19, 2026

Connections

- When a connector test or schema refresh hits an unexpected internal error, the job now fails immediately with a clear error message instead of appearing to run until it times out.

## August 18, 2026

Connections

- Setting up or refreshing the schema for a source with a very large number of tables and columns is now more reliable. Previously, these requests could run out of memory and fail before the schema reached you.

## August 14, 2026

Connections

- Your connections now recover immediately when Airbyte runs into a conflict while starting a sync. Previously, the connection paused for about 10 minutes in this situation, which delayed its next scheduled sync.

Connector Builder

- Fields that share a linked value keep that link when you switch between the UI and YAML views. Previously, the first switch to YAML could replace shared values with copies, so later edits to one field no longer updated the others.

## August 12, 2026

Connections

- When you set up a new source or destination, Airbyte now opens the configuration form first instead of the AI setup assistant. You can still switch to the assistant at any time with the Agent/Form toggle at the top of the page.

## August 11, 2026

Platform

- Airbyte Cloud now uses a new cookie consent tool. You see a redesigned consent banner on your first visit, and you can still change your choices at any time with the Cookie preferences option in your user settings.

## August 7, 2026

Connections

- Some syncs now run faster. Airbyte correctly reads the processing capacity allotted to a sync and opens as many parallel data channels as that capacity allows, instead of falling back to a single channel.

## August 6, 2026

API

- Not-found (404) error responses in the API no longer declare a message as required. If you generate a client from Airbyte's API spec, those clients no longer fail to parse a not-found response that comes back without a message.

## August 5, 2026

Platform

- You can now assign two new workspace roles from the Members page: Source editor and Destination editor. A source editor can create and edit a workspace's sources and connections but not its destinations, and a destination editor can do the reverse. Both roles are available on the Pro and Enterprise Flex plans.

## August 3, 2026

Platform

- Your Data Worker usage now reflects only the capacity your syncs are actually using. Previously, if a job reached a failed or cancelled state moments before Airbyte recorded its capacity reservation, that capacity stayed reserved indefinitely, overstating your organization's usage and leaving less capacity available for new syncs.

## July 27, 2026

Platform

- The invitation code that lets someone join your organization or workspace is now sent only to the person you invited. It's no longer visible to anyone viewing your list of pending invitations, so only the intended recipient can accept an invitation. Inviting, viewing, and canceling pending invitations in Settings works exactly as before.

## July 23, 2026

Connections

- When you set up a new connection, Airbyte now warns you that the initial sync replicates all data in every enabled stream, which can mean a large volume of historical data. Because Airbyte Cloud bills based on data replicated, enable only the streams and fields you need, and if your source supports a replication start date, set a recent one to limit how much history is synced.
- You can now complete OAuth authorization for the Amazon Seller Partner source when your Seller or Vendor account is in the Ireland (IE) region. Previously, starting the authorization for an Ireland-based account produced an invalid consent link.

## July 17, 2026

Connections

- When you connect a source that authenticates through OAuth and the authorization is denied or fails, Airbyte no longer saves an invalid credential. The error is now surfaced so you can correct the problem and try again.

Platform

- If you're invited to an organization but don't yet belong to one, the app now loads correctly so you can view and accept your invitation. Previously these screens could fail to load when your account had no current organization.

## July 14, 2026

Connector Builder

- When you test a stream in the Connector Builder, the test button now checks for configuration errors only in the stream you're testing, along with your global and user input settings. You can now test a stream even when a different stream in the same connector still has errors.

Platform

- If your organization uses single sign-on (SSO), sign-ins are now rejected when your identity provider presents a user whose email domain your organization hasn't verified. This prevents unverified email domains from being used to access your organization.
