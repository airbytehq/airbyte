---
sidebar_position: 1
sidebar_label: Lovable
---

# Lovable

[Lovable](https://lovable.dev) is an AI app builder that generates full-stack React and Supabase applications from natural-language prompts. Lovable doesn't expose a dedicated "skills" surface, but you can give it the same context two different ways: paste the skill directly into the prompt you use to build the app, or add it to Project/Workspace Knowledge.

The Airbyte skill for Lovable is a single Markdown document that teaches Lovable how to wire up two Supabase Edge Functions (for server-side token exchange and connector execution), the Airbyte embedded widget (for end-user connector setup), and a React query hook (for reading and writing data). Once Lovable has the skill in context, you can ask it to build apps against any of Airbyte's connectors without explaining the integration yourself.

## Add the skill to Lovable

In testing, pasting the skill directly into the initial build prompt produces the most reliable results. Lovable's Knowledge surfaces (Project Knowledge and Workspace Knowledge) work as a fallback, but Lovable doesn't always apply Knowledge consistently on every generation, so prefer the prompt approach.

### Recommended: paste it into the build prompt

1. In the Lovable chat, open a new prompt for the app you want to build.
2. Copy the entire skill text from [The skill](#the-skill) section below and paste it at the top of the prompt.
3. Below the skill text, add your build instructions. For example: _"Using the preceding Airbyte integration context, build a page that lets the user connect their Stripe account with the Airbyte widget and then lists their customers."_
4. Send the prompt. Lovable generates the Edge Functions, the widget setup, and the query code based on the skill.

### Alternative: add it to project knowledge

Use this if you want the skill available to every prompt in a project or across your workspace. Lovable applies Knowledge less reliably than in-prompt context, so expect occasional drift.

1. Open your project in Lovable.
2. Go to **Project settings** > **Knowledge**. To apply the skill across all your Lovable projects, use **Workspace Knowledge** instead.
3. Copy the entire skill text from [The skill](#the-skill) section below and paste it into the project knowledge (or workspace knowledge) text area. Lovable auto-saves your entry.
4. In the Lovable chat, prompt the AI with something like: _"Using the Airbyte integration in the project knowledge, build a page that lists Stripe customers."_

## Configure Supabase secrets

The skill relies on two secrets in your Supabase project. Set these in the Supabase dashboard under **Settings** > **Edge Functions** > **Secrets** before you run the generated code:

- `AIRBYTE_CLIENT_ID`
- `AIRBYTE_CLIENT_SECRET`

Get these from your Airbyte dashboard at [app.airbyte.ai](https://app.airbyte.ai).

## The skill

Copy everything in the block below and paste it into your Lovable build prompt (or into a Knowledge entry if you chose that path).

`````markdown
# Airbyte Integration for Lovable Apps

Airbyte provides managed connectors to 500+ SaaS APIs (Stripe, HubSpot, Jira, Salesforce, GitHub, Zendesk, etc.). Use it to read and write data from these services without building API integrations yourself.

**Architecture**: Two Supabase Edge Functions handle all server-side work. The Airbyte widget (npm package) handles connector setup UI. Your React app calls the Edge Functions for data.

**Connector reference docs**: Each connector's supported entities, actions, and params are documented at `https://docs.airbyte.com/ai-agents/connectors/{connector-name}/REFERENCE.md` (e.g. `.../salesforce/REFERENCE.md`, `.../stripe/REFERENCE.md`). Share this link with the user to look up exact field names and parameters.

## Dependencies

```bash
npm install @airbyte-embedded/airbyte-embedded-widget
```

## Supabase Secrets

Set in Supabase dashboard under Settings > Edge Functions > Secrets:

| Secret | Description |
|--------|-------------|
| `AIRBYTE_CLIENT_ID` | Client ID from the Airbyte dashboard |
| `AIRBYTE_CLIENT_SECRET` | Client secret from the Airbyte dashboard |

## Edge Function: `airbyte-token`

Returns widget tokens (for connector setup) or scoped tokens (for listing connectors). Never exposes access tokens to the browser.

Create `supabase/functions/airbyte-token/index.ts`:

```typescript
// Deno URL import — Edge Functions run on Deno, not Node.
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const AIRBYTE_API = "https://api.airbyte.ai";
const CLIENT_ID = Deno.env.get("AIRBYTE_CLIENT_ID")!;
const CLIENT_SECRET = Deno.env.get("AIRBYTE_CLIENT_SECRET")!;

// Safe: credentials stay server-side. For production, replace "*" with your app's origin.
const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

async function getAccessToken(): Promise<string> {
  const res = await fetch(`${AIRBYTE_API}/api/v1/account/applications/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET }),
  });
  if (!res.ok) throw new Error(`Token exchange failed: ${res.status}`);
  return (await res.json()).access_token;
}

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const type = new URL(req.url).searchParams.get("type") ?? "widget";
    const body = await req.json();
    const token = await getAccessToken();
    const endpoint = type === "scoped"
      ? `${AIRBYTE_API}/api/v1/account/applications/scoped-token`
      : `${AIRBYTE_API}/api/v1/account/applications/widget-token`;
    const payload = type === "scoped"
      ? { workspace_name: body.workspace_name }
      : { workspace_name: body.workspace_name, allowed_origin: body.allowed_origin };
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
    return json(await res.json(), res.status);
  } catch (err) {
    return json({ error: (err as Error).message }, 502);
  }
});
```

## Edge Function: `airbyte-execute`

Proxies data read/write operations. Obtains its own access token server-side.

Create `supabase/functions/airbyte-execute/index.ts`:

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const AIRBYTE_API = "https://api.airbyte.ai";
const CLIENT_ID = Deno.env.get("AIRBYTE_CLIENT_ID")!;
const CLIENT_SECRET = Deno.env.get("AIRBYTE_CLIENT_SECRET")!;

// Safe: credentials stay server-side. For production, replace "*" with your app's origin.
const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

async function getAccessToken(): Promise<string> {
  const res = await fetch(`${AIRBYTE_API}/api/v1/account/applications/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET }),
  });
  if (!res.ok) throw new Error(`Token exchange failed: ${res.status}`);
  return (await res.json()).access_token;
}

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const { connector_id, entity, action, params } = await req.json();
    const token = await getAccessToken();
    // IMPORTANT: path must be /api/v1/integrations/connectors/... (not /api/public/v1/connectors/...)
    const res = await fetch(
      `${AIRBYTE_API}/api/v1/integrations/connectors/${connector_id}/execute`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ entity, action, params: params ?? {} }),
      }
    );
    return json(await res.json(), res.status);
  } catch (err) {
    return json({ error: (err as Error).message }, 502);
  }
});
```

## Widget Integration

```typescript
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";
import { useCallback, useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export function useAirbyteWidget({ workspaceName }: { workspaceName: string }) {
  const widgetRef = useRef<AirbyteEmbeddedWidget | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [sourceId, setSourceId] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const { data } = await supabase.functions.invoke("airbyte-token", {
        body: { workspace_name: workspaceName, allowed_origin: window.location.origin },
      });
      if (cancelled || !data?.token) return;
      widgetRef.current = new AirbyteEmbeddedWidget({
        token: data.token,
        onEvent: (event: any) => {
          // Widget emits { type: "sourceCreated", data: { sourceId, sourceName, ... } }
          if (event?.type === "sourceCreated") {
            setSourceId(event.data?.sourceId); // connector_id for execute
          }
        },
      });
      setIsReady(true);
    })();
    return () => { cancelled = true; widgetRef.current?.destroy(); };
  }, [workspaceName]);
  const open = useCallback(() => widgetRef.current?.open(), []);
  return { open, isReady, sourceId };
}
```

## Querying Data

```typescript
import { useCallback, useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export function useAirbyteQuery<T = unknown>(
  connectorId: string | null, entity: string, action: string, params?: Record<string, unknown>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetch_ = useCallback(async () => {
    if (!connectorId) return;
    setLoading(true);
    setError(null);
    try {
      const { data: response, error: fnError } = await supabase.functions.invoke("airbyte-execute",
        { body: { connector_id: connectorId, entity, action, params } });
      if (fnError) throw fnError;
      if (response.status !== "success") throw new Error(response.result?.error ?? "Execute failed");
      // context_store_search wraps records in { data: [...], meta: {...} }; list returns the array directly
      setData((response.result?.data ?? response.result) as T);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [connectorId, entity, action, JSON.stringify(params)]);
  useEffect(() => { fetch_(); }, [fetch_]);
  return { data, loading, error, refetch: fetch_ };
}
```

## Choosing an Action

**Not every connector supports every action for every entity.** Check the connector's REFERENCE.md.

| Action | When to use |
|--------|-------------|
| `list` | **Default after widget setup.** Live API — works immediately, no sync needed. |
| `context_store_search` | **Default for existing connectors.** Searches synced data with filters/sorting. Requires first sync to complete (automatic, takes a few minutes). Fetch by ID: `{ query: { filter: { eq: { Id: "..." } } }, limit: 1 }` |
| `get` | Fetch one record by ID — **only if REFERENCE.md lists it.** Params: `{ id: "..." }`. Otherwise use `context_store_search` with `eq`. |
| `api_search` | Connector-native search (Salesforce SOSL, Jira JQL). Params vary — check REFERENCE.md. |
| `create` | Create a record. Params: the record fields. |
| `update` | Update a record. Params: `{ id: "...", ...fields }` |
| `delete` | Delete a record. Params: `{ id: "..." }` |

## Searching Data (Context Store)

Use `context_store_search` for connectors that have already synced (returning users, not fresh widget setup).

```typescript
const { data } = useAirbyteQuery(connectorId, "customers", "context_store_search", {
  query: {
    filter: { like: { email: "%@acme.com" } },
    sort: [{ created_at: "desc" }],
  },
  limit: 50,
  fields: ["id", "name", "email"],
});
```

**Filter operators**: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `like` (SQL `%` wildcards), `fuzzy` (ordered word match), `keyword` (any word present), `in` (value in list). Combine with `and`, `or`, `not`. Advanced operators (`any`, `has`, `contains` for nested/array fields) — see the connector's REFERENCE.md.

## Write Operations

```typescript
await supabase.functions.invoke("airbyte-execute", {
  body: { connector_id: connectorId, entity: "customers", action: "create",
    params: { name: "Jane Doe", email: "jane@example.com" } },
});
```
`````

## Source

Airbyte keeps the canonical version of this skill in the [airbytehq/sonar](https://github.com/airbytehq/sonar) repository at [`docs/airbyte-for-lovable.md`](https://github.com/airbytehq/sonar/blob/main/docs/airbyte-for-lovable.md). Check there for the latest version.
