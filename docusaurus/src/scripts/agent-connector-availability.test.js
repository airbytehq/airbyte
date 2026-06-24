const assert = require("assert");
const {
  extractEnabledAgentConnectorSlugs,
  getConnectorSlug,
  isEnabledConnector,
  slugifyConnectorName,
} = require("./agent-connector-availability");

function testSlugifyConnectorName() {
  assert.strictEqual(
    slugifyConnectorName("PayPal Transaction"),
    "paypal-transaction",
  );
  assert.strictEqual(slugifyConnectorName("Zoho_CRM"), "zoho-crm");
}

function testGetConnectorSlug() {
  assert.strictEqual(
    getConnectorSlug({
      connector_name: "fallback-name",
      docs_url:
        "https://raw.githubusercontent.com/airbytehq/airbyte-agent-sdk/refs/heads/main/connectors/linkedin-ads/REFERENCE.md",
    }),
    "linkedin-ads",
  );
}

function testIsEnabledConnector() {
  assert.strictEqual(isEnabledConnector({ connector_name: "stripe" }), true);
  assert.strictEqual(
    isEnabledConnector({
      connector_name: "shopify",
      platform_availability: { state: "experimental" },
    }),
    false,
  );
  assert.strictEqual(
    isEnabledConnector({
      connector_name: "future-state",
      platform_availability: { state: "private_preview" },
    }),
    false,
  );
}

function testExtractEnabledAgentConnectorSlugs() {
  const registry = {
    connectors: [
      { connector_name: "stripe", platform_availability: { state: "enabled" } },
      {
        connector_name: "shopify",
        platform_availability: { state: "experimental" },
      },
      { connector_name: "paypal-transaction" },
      {
        connector_name: "future-state",
        platform_availability: { state: "private_preview" },
      },
    ],
  };

  assert.deepStrictEqual(
    extractEnabledAgentConnectorSlugs(registry, [
      "future-state",
      "paypal-transaction",
      "shopify",
      "stripe",
    ]),
    ["paypal-transaction", "stripe"],
  );
}

testSlugifyConnectorName();
testGetConnectorSlug();
testIsEnabledConnector();
testExtractEnabledAgentConnectorSlugs();

console.log("agent connector availability tests passed");
