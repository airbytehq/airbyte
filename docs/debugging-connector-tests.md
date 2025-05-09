# Debugging Connector Tests in GitHub Actions

This guide explains how to debug connector tests in GitHub Actions using SSH access.

## How to Debug Connector Tests

When you need to debug connector tests failing in GitHub Actions, you can enable an SSH session directly in the workflow using tmate. This lets you connect to the runner and troubleshoot in real-time.

### Option 1: Using the Manual Workflow Dispatch

1. Go to the **Actions** tab in your GitHub repository
2. Select the **Connector CI (Beta)** workflow
3. Click **Run workflow** and set these parameters:
   - Enable the **enable-debug** checkbox
   - Run from your branch/PR
   - Click **Run workflow**

### Option 2: Add to PR Comment

You can trigger debugging by adding a comment to your PR:

```
/connector-test --enable-debug
```

## Connecting to the SSH Session

When the workflow runs with debugging enabled:

1. Look for the **Setup tmate SSH session** step in the workflow run
2. You'll see SSH connection information displayed in the workflow logs:
   ```
   SSH: ssh <connection-string>
   Web URL: https://tmate.io/<session-id>
   ```
3. Use either method to connect to the session:
   - SSH in your terminal: `ssh <connection-string>`
   - Open the web URL in your browser for a web terminal

## Using the Debug Session

Once connected, you'll have shell access to debug your connector:

1. You'll be in the GitHub Actions environment with all dependencies installed
2. Navigate to your connector directory: `cd airbyte-integrations/connectors/<your-connector>`
3. Run tests manually:
   ```bash
   # Run unit tests
   poe test-unit-tests
   
   # Run integration tests
   poe test-integration-tests
   ```
4. Check environment variables, secrets, etc.

## Important Notes

- The session will pause the GitHub workflow while you're connected
- The session will automatically time out after a period of inactivity
- Any code changes made during the session won't be saved back to your repository
- Be mindful of usage as debugging sessions consume GitHub Actions minutes
- SSH sessions are limited to the user who opened the PR (for security)

## Troubleshooting SSH Connection

If you have trouble connecting:

- Ensure your SSH client is properly configured
- Try the web URL option if SSH is blocked by your network
- Check GitHub logs for any connection issues
- Make sure the debug step completed successfully in the workflow

Remember to exit the session after you're done debugging to allow the workflow to continue.