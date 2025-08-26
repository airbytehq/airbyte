---
products: embedded
---

# 2-Minute Quickstart

## Setup (all apps)

### Clone and install dependencies for all apps
```bash
git clone https://github.com/airbytehq/embedded-demo.git
cd embedded-demo
npm install
```

```bash
cd apps/server
cp .env.example .env
# Edit .env with your credentials
```

## Run all apps
```bash
# From root directory - starts all apps simultaneously
npm run dev

→ Server & Vanilla JS: http://localhost:3000
→ Next.js: http://localhost:3001
→ React: http://localhost:3002
```

## Run individual apps
```bash
# Run only the server
npm run dev --filter=@airbyte-demo/server

# Run only React app  
npm run dev --filter=@airbyte-demo/reactjs

# Run only Next.js app
npm run dev --filter=@airbyte-demo/nextjs
```

## Get your credentials
Contact Airbyte: Reach out to michel@airbyte.io or teo@airbyte.io for Embedded access.
Get your keys: You'll receive your organization ID, client ID, and client secret.
Update config: Add them to your `.env` file:
```bash
# server/.env
SONAR_AIRBYTE_WEBAPP_PASSWORD=your_demo_password
SONAR_AIRBYTE_ALLOWED_ORIGIN=http://localhost:3000
SONAR_AIRBYTE_ORGANIZATION_ID=your_organization_id
SONAR_AIRBYTE_CLIENT_ID=your_client_id
SONAR_AIRBYTE_CLIENT_SECRET=your_client_secret
```


