/**
 * Utility to fetch connector quality metrics for docs header decorations.
 *
 * Metrics are exported as JSONL in GCS. This module lists the metrics prefix,
 * picks the latest JSONL object by name, parses it by connector definition ID
 * and Airbyte platform, and caches the slimmed nested map for the Docusaurus
 * build.
 */
const crypto = require("crypto");
const fs = require("fs");
const https = require("https");
const {
  DATA_DIR,
  CONNECTOR_QUALITY_METRICS_CACHE_PATH,
  CONNECTOR_QUALITY_METRICS_BUCKET,
  CONNECTOR_QUALITY_METRICS_PREFIX,
} = require("./constants");

const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";
const GCS_READ_ONLY_SCOPE = "https://www.googleapis.com/auth/devstorage.read_only";

let inMemoryMetrics = null;
let inMemoryAccessToken = null;

function base64UrlEncode(value) {
  return Buffer.from(value)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function requestText(url, options = {}) {
  return new Promise((resolve, reject) => {
    const request = https.request(url, options, (response) => {
      let data = "";

      response.on("data", (chunk) => {
        data += chunk;
      });

      response.on("end", () => {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new Error(`Request failed for ${url}: ${response.statusCode}`));
          return;
        }

        resolve(data);
      });
    });

    request.on("error", (error) => {
      reject(new Error(`Network error fetching ${url}: ${error.message}`));
    });

    if (options.body) {
      request.write(options.body);
    }

    request.end();
  });
}

async function requestJson(url, options = {}) {
  const text = await requestText(url, options);
  return JSON.parse(text);
}

function readServiceAccountCredentials() {
  const credentialsJson =
    process.env.GCS_CREDENTIALS || process.env.GCP_GSM_CREDENTIALS;

  if (credentialsJson) {
    return JSON.parse(credentialsJson);
  }

  if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
    return JSON.parse(
      fs.readFileSync(process.env.GOOGLE_APPLICATION_CREDENTIALS, "utf8"),
    );
  }

  return null;
}

async function getGoogleAccessToken() {
  if (inMemoryAccessToken) {
    return inMemoryAccessToken;
  }

  const credentials = readServiceAccountCredentials();
  if (!credentials?.client_email || !credentials?.private_key) {
    return null;
  }

  const now = Math.floor(Date.now() / 1000);
  const header = base64UrlEncode(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claimSet = base64UrlEncode(
    JSON.stringify({
      iss: credentials.client_email,
      scope: GCS_READ_ONLY_SCOPE,
      aud: GOOGLE_TOKEN_URL,
      exp: now + 3600,
      iat: now,
    }),
  );
  const unsignedToken = `${header}.${claimSet}`;
  const signature = crypto
    .createSign("RSA-SHA256")
    .update(unsignedToken)
    .sign(credentials.private_key);
  const assertion = `${unsignedToken}.${base64UrlEncode(signature)}`;
  const body = new URLSearchParams({
    grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
    assertion,
  }).toString();

  const tokenResponse = await requestJson(GOOGLE_TOKEN_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Content-Length": Buffer.byteLength(body),
    },
    body,
  });
  inMemoryAccessToken = tokenResponse.access_token;
  return inMemoryAccessToken;
}

async function getGcsRequestHeaders() {
  const accessToken = await getGoogleAccessToken();
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function buildGcsListUrl() {
  const params = new URLSearchParams({
    prefix: CONNECTOR_QUALITY_METRICS_PREFIX,
    fields: "items(name,updated)",
  });
  return `https://storage.googleapis.com/storage/v1/b/${CONNECTOR_QUALITY_METRICS_BUCKET}/o?${params}`;
}

function buildGcsObjectUrl(objectName) {
  const encodedObjectName = encodeURIComponent(objectName);
  return `https://storage.googleapis.com/storage/v1/b/${CONNECTOR_QUALITY_METRICS_BUCKET}/o/${encodedObjectName}?alt=media`;
}

function getLatestJsonlObjectName(listResponse) {
  return (listResponse.items || [])
    .map((item) => item.name)
    .filter((name) => name.endsWith(".jsonl"))
    .sort()
    .reverse()[0];
}

function convertStringNullValues(data) {
  return Object.fromEntries(
    Object.entries(data).map(([key, value]) => [
      key,
      value === "null" ? null : value,
    ]),
  );
}

function parseConnectorMetricsJsonl(jsonlText) {
  const metricsByDefinitionId = {};

  for (const line of jsonlText.split(/\r?\n/)) {
    if (!line.trim()) {
      continue;
    }

    const connectorData = JSON.parse(line)._airbyte_data;
    const connectorDefinitionId = connectorData?.connector_definition_id;
    const airbytePlatform = connectorData?.airbyte_platform;

    if (!connectorDefinitionId || !airbytePlatform) {
      continue;
    }

    metricsByDefinitionId[connectorDefinitionId] ||= {};
    metricsByDefinitionId[connectorDefinitionId][airbytePlatform] =
      convertStringNullValues(connectorData);
  }

  return metricsByDefinitionId;
}

async function fetchConnectorQualityMetricsFromRemote() {
  const headers = await getGcsRequestHeaders();
  const listResponse = await requestJson(buildGcsListUrl(), { headers });
  const latestObjectName = getLatestJsonlObjectName(listResponse);

  if (!latestObjectName) {
    return {};
  }

  const latestMetricsJsonl = await requestText(
    buildGcsObjectUrl(latestObjectName),
    {
      headers,
    },
  );
  return parseConnectorMetricsJsonl(latestMetricsJsonl);
}

async function fetchConnectorQualityMetrics() {
  if (inMemoryMetrics) {
    return inMemoryMetrics;
  }

  if (fs.existsSync(CONNECTOR_QUALITY_METRICS_CACHE_PATH)) {
    inMemoryMetrics = JSON.parse(
      fs.readFileSync(CONNECTOR_QUALITY_METRICS_CACHE_PATH, "utf8"),
    );
    return inMemoryMetrics;
  }

  try {
    inMemoryMetrics = await fetchConnectorQualityMetricsFromRemote();
  } catch (error) {
    console.warn(
      `Connector quality metrics unavailable; docs will omit connector metric badges. ${error.message}`,
    );
    inMemoryMetrics = {};
  }

  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  fs.writeFileSync(
    CONNECTOR_QUALITY_METRICS_CACHE_PATH,
    JSON.stringify(inMemoryMetrics, null, 2),
  );
  console.log(
    `✓ Cached connector quality metrics for ${Object.keys(inMemoryMetrics).length} connectors`,
  );

  return inMemoryMetrics;
}

module.exports = {
  fetchConnectorQualityMetrics,
  fetchConnectorQualityMetricsFromRemote,
  getLatestJsonlObjectName,
  parseConnectorMetricsJsonl,
};
