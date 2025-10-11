# Prerequisites for Airbyte AI Agents

Before you start building AI agents with Airbyte Embedded, ensure you have the following prerequisites in place.

## Account Requirements

### Airbyte Account
- **Self-Managed Enterprise** or **Airbyte Cloud Enterprise** account
- Airbyte Embedded features are available on Enterprise plans only
- [Contact Sales](https://airbyte.com/company/talk-to-sales) if you need to upgrade

### Access Credentials
You'll need the following credentials to use Airbyte's APIs:
- **Organization ID** - Your organization identifier
- **Client ID** - Application client identifier
- **Client Secret** - Application secret key

## Technical Requirements

### API Access Setup

1. **Configure API Access**
   - Navigate to your Airbyte instance
   - Go to Settings > Developer Settings
   - Create a new application or use an existing one
   - Save your Client ID and Client Secret securely

2. **Generate Access Token**
   ```bash
   curl -X POST https://api.airbyte.com/v1/applications/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "YOUR_CLIENT_ID",
       "client_secret": "YOUR_CLIENT_SECRET"
     }'
   ```

   Response:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

3. **Test API Access**
   ```bash
   curl -X GET https://api.airbyte.com/v1/workspaces \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

### Development Environment

#### For Embedded Widget Integration
- **Node.js** 16+ or **npm** 8+
- **React** 18+ (recommended) or vanilla JavaScript
- Modern browser with JavaScript enabled
- HTTPS endpoint for production (required for secure token handling)

#### For Headless API Integration
- **Programming Language**: Python 3.8+, Node.js 16+, or any language with HTTP client
- **HTTP Client Library**:
  - Python: `requests` or `httpx`
  - JavaScript: `fetch` or `axios`
  - Other: Any HTTP/REST client
- **JSON Processing**: Native JSON support in your language

### Network Requirements

1. **Outbound Access**
   - Your application must be able to reach `api.airbyte.com` (or your self-hosted instance)
   - Port 443 (HTTPS) must be accessible
   - Websocket connections (for real-time updates in widget)

2. **CORS Configuration** (for browser-based applications)
   - Ensure your domain is whitelisted in Airbyte settings
   - Configure appropriate CORS headers

## Workspace Setup

### Create a Workspace

Every integration requires at least one workspace. Workspaces provide isolation between different customers or environments.

**Single-Tenant Architecture:**
```
Organization
└── Workspace (per customer)
    ├── Sources
    ├── Destinations
    └── Connections
```

**Multi-Tenant Architecture:**
```
Organization
├── Workspace (Customer A)
│   ├── Sources
│   └── Connections
├── Workspace (Customer B)
│   ├── Sources
│   └── Connections
└── Workspace (Customer C)
    ├── Sources
    └── Connections
```

### Create Your First Workspace

```bash
curl -X POST https://api.airbyte.com/v1/workspaces \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First AI Agent Workspace",
    "organizationId": "YOUR_ORGANIZATION_ID"
  }'
```

## Security Considerations

### Token Management
- **Never expose** Client ID and Client Secret in client-side code
- **Never commit** credentials to version control
- **Use environment variables** for storing sensitive credentials
- **Implement token refresh** logic for long-running applications
- **Generate user-scoped tokens** for embedded scenarios (see authentication guide)

### Data Isolation
- **Use separate workspaces** for different customers (recommended)
- **Implement proper access control** using permissions API
- **Validate user permissions** before granting access to resources

### Best Practices
- Store credentials in a secure secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate credentials regularly
- Use HTTPS for all API communications
- Implement rate limiting in your application
- Log API access for audit purposes

## Next Steps

Once you have completed these prerequisites:

1. **Choose Your Integration Path**
   - [Embedded Widget](./widget/README.md) - Pre-built UI component for source configuration
   - [Headless API](./api/README.md) - Build custom UI with direct API integration

2. **Follow the Quickstart Guide**
   - [Quickstart: Build Your First AI Agent](../quickstart.md)

3. **Explore Advanced Topics**
   - [Authentication & Authorization](./api/authentication.md)
   - [Connection Templates](./api/connection-templates.md)
   - [Source Templates](./api/source-templates.md)

## Troubleshooting

### Cannot Generate Access Token
**Symptom:** API returns 401 Unauthorized when trying to generate token

**Solution:**
- Verify your Client ID and Client Secret are correct
- Check that your application is active in Airbyte settings
- Ensure you're using the correct API endpoint (Cloud vs Self-Hosted)

### Cannot Access API Endpoints
**Symptom:** API returns 403 Forbidden for workspace operations

**Solution:**
- Verify your access token is valid and not expired
- Check that your organization has the required Enterprise plan
- Ensure your application has the necessary permissions

### CORS Errors in Browser
**Symptom:** Browser console shows CORS policy errors

**Solution:**
- Verify your domain is whitelisted in Airbyte CORS settings
- Ensure you're making requests from an HTTPS origin in production
- For development, use a proxy or configure local CORS settings

## Additional Resources

- [Airbyte API Documentation](https://reference.airbyte.com)
- [Authentication Guide](./api/authentication.md)
- [Airbyte Cloud Documentation](https://docs.airbyte.com)
- [Contact Support](https://airbyte.com/support)
