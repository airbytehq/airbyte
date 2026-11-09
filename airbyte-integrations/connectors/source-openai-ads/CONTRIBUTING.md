# Contributing to source-openai-ads

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **API-Key Authentication and OAuth Roadmap** — API keys are scoped to one ad account; OAuth appears in OpenAI's spec but is not yet supported by the connector ([authentication](https://developers.openai.com/ads/api-reference/authentication), [OpenAPI security scheme](https://developers.openai.com/ads/openapi.json#/components/securitySchemes/AdsOAuth), [certification epic](https://github.com/airbytehq/airbyte-internal-issues/issues/18388)).
2. **Vendor Error Mapping** — Only pixel-management `404`s and spend-limit `403`s are skipped; rate limits and server errors are retried ([partner setup](https://developers.openai.com/ads/api-partner-setup), [ad account](https://developers.openai.com/ads/api-reference/ad-account), [rate limits](https://developers.openai.com/ads/api-overview#rate-limits)).
3. **Shared 600-Request Rate Limit** — The connector stays below OpenAI's per-endpoint and overall limits, while Cloud connections share IP-scoped quota ([rate limits](https://developers.openai.com/ads/api-overview#rate-limits), [Cloud IP allow list](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist)).
4. **Full-Refresh Entities and Incremental Reports** — Entity lists are full refresh, while insights and conversions reports use incremental date windows ([OpenAPI spec](https://developers.openai.com/ads/openapi.json), [insights API](https://developers.openai.com/ads/api-reference/insights), [reporting](https://developers.openai.com/ads/reporting)).
5. **Endpoint-Specific Pagination Limits** — List and insights endpoints have different page limits, and conversions insights requires one entity per request ([OpenAPI spec](https://developers.openai.com/ads/openapi.json), [insights API](https://developers.openai.com/ads/api-reference/insights)).
6. **Mock-Only Testing** — No test credential or vendor sandbox is available, so unit tests use `requests_mock` ([authentication](https://developers.openai.com/ads/api-reference/authentication), [tracking issue](https://github.com/airbytehq/airbyte-internal-issues/issues/18389)).
