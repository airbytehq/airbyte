# Airbyte WebApp 1.7.8: `new-source` TypeError (`reading 'sort'`)

## Reported error payload

```json
{
  "url": "https://abc.airbyte.com/workspaces/850e0099-1f1e-4404-821f-c1246adee09a/source/new-source",
  "airbyteVersion": "1.7.8",
  "errorType": "TypeError",
  "errorConstructor": "TypeError",
  "error": {},
  "stacktrace": "TypeError: Cannot read properties of undefined (reading 'sort')\n    at https://abc.airbyte.comassets/core-bxruo5x4p5.js:388:105192\n    at async Object.queryFn (https://abc.airbyte.comassets/core-bxruo5x4p5.js:388:105127)",
  "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
  "featureFlags": {}
}
```

## Fix pattern

The crash happens when `queryFn` receives an undefined list and calls `.sort()` directly.
Use a null-safe fallback before sorting.

```ts
const connectors = (response?.connectors ?? []).slice().sort(sortByDisplayName);
```

Equivalent safe forms are acceptable as long as `.sort()` is never called on `undefined`.

## Validation notes

- Repro URL: `/workspaces/:id/source/new-source`
- Before: uncaught `TypeError` in `queryFn`.
- After: page renders, list remains sorted when data exists.