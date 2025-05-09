# Debugging GitHub Actions with SSH

This guide explains how to debug connector tests in GitHub Actions using SSH access via tmate.

## How to Debug Connector Tests

1. **Trigger the Debug Workflow**:
   - Go to the Actions tab in your GitHub repository
   - Select "Debug Connector Tests" workflow
   - Click "Run workflow"
   - Enter the required parameters:
     - `connector`: Name of the connector to debug (e.g., `source-postgres`)
     - `test-type`: Type of test to run (`unit`, `integration`, or `both`)
     - `wait-for-ssh`: Whether to wait for SSH connection before continuing (default: `true`)
     - `timeout-minutes`: How long to keep the session open (default: `30` minutes)

2. **Connect to the SSH Session**:
   - When the workflow runs, it will display SSH connection information in the workflow logs
   - You'll see both SSH and Web URL options to connect to the session:
     ```
     SSH: ssh <connection-string>
     Web URL: https://tmate.io/<session-id>
     ```

3. **Debugging Within the Session**:
   - Once connected, you'll have shell access to the GitHub Actions runner
   - Navigate to your connector directory: `cd airbyte-integrations/connectors/<your-connector>`
   - Run tests manually with commands like:
     ```bash
     poe test-unit-tests
     poe test-integration-tests
     ```
   - Inspect logs, modify code, and debug issues

4. **Ending the Session**:
   - The session will automatically terminate after the specified timeout
   - To end manually, type `exit` in the SSH session or close the browser tab
   - The workflow will continue with any remaining steps after the session ends

## Tips for Effective Debugging

- **Start Small**: First test with unit tests before moving to integration tests
- **Check Environment**: Verify secrets are properly loaded with `env | grep -i secret`
- **Log Inspection**: Check logs in the runner for any configuration issues
- **Code Changes**: Any changes made in the SSH session won't be committed back to your repo
- **Security**: Never share your SSH connection strings publicly

## Modifying the Debug Workflow

If you need to customize the debug workflow for specific connectors or test scenarios:

1. Edit the `.github/workflows/debug-connector-test.yml` file
2. Adjust the environment setup steps as needed
3. Add any specific testing commands or environment variables required

## Troubleshooting

- **Can't Connect**: Ensure your IP is allowed by your organization's security policies
- **Authentication Issues**: Check that your GitHub token has sufficient permissions
- **Secrets Not Available**: Verify that the necessary secrets are available to the workflow

Remember that SSH sessions in GitHub Actions consume runner minutes, so use them wisely!