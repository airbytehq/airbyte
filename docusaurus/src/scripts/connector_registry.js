const memoize = require("lodash/memoize");

/**
 * Fetch with retry logic and exponential backoff
 * @param {string} url - URL to fetch
 * @param {object} options - Retry options
 * @returns {Promise<object|null>} - Parsed JSON response or null on failure
 */
async function fetchWithRetry(url, options = {}) {
  const {
    attempts = 3,
    delays = [1000, 5000, 15000],
    timeoutMs = 10000,
    connectorName = null,
  } = options;

  const connectorContext = connectorName ? ` for connector: ${connectorName}` : "";

  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      console.log(
        `[PyPI Fetch] Attempt ${attempt}/${attempts}${connectorContext}${attempt > 1 ? ` after ${delays[attempt - 2]}ms delay` : ""}`,
      );

      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          "User-Agent": "Airbyte-Docusaurus-Build",
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unable to read response");
        console.warn(
          `[PyPI Fetch] Attempt ${attempt}/${attempts} failed: HTTP ${response.status} ${response.statusText}${connectorContext}`,
        );
        
        if (attempt === attempts) {
          console.error(
            `[PyPI Fetch] All ${attempts} attempts failed. Last error: HTTP ${response.status}${connectorContext}`,
          );
          return null;
        }

        const delay = delays[attempt - 1];
        const jitter = Math.random() * 200;
        await new Promise((resolve) => setTimeout(resolve, delay + jitter));
        continue;
      }

      const json = await response.json();
      console.log(`[PyPI Fetch] Success on attempt ${attempt}/${attempts}${connectorContext}`);
      return json;
    } catch (error) {
      const errorType = error.name === "AbortError" ? "Timeout" : error.name;
      console.warn(
        `[PyPI Fetch] Attempt ${attempt}/${attempts} failed: ${errorType} - ${error.message}${connectorContext}`,
      );

      if (attempt === attempts) {
        console.error(
          `[PyPI Fetch] All ${attempts} attempts failed. Last error: ${errorType} - ${error.message}${connectorContext}`,
        );
        return null;
      }

      const delay = delays[attempt - 1];
      const jitter = Math.random() * 200;
      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
    }
  }

  return null;
}

const fetchLatestVersionOfPyPackage = memoize(async (packageName, connectorName = null) => {
  const json = await fetchWithRetry(
    `https://pypi.org/pypi/${packageName}/json`,
    { connectorName },
  );

  if (!json || !json.info || !json.info.version) {
    console.warn(
      `[PyPI Fetch] Unable to determine version for package: ${packageName}`,
    );
    return null;
  }

  return json.info.version;
});

const getLatestPythonCDKVersion = async (connectorName = null) =>
  fetchLatestVersionOfPyPackage("airbyte-cdk", connectorName);

const parseCDKVersion = (
  connectorCdkVersion,
  latestPythonCdkVersion,
  latestJavaCdkVersion,
) => {
  if (!connectorCdkVersion || !connectorCdkVersion.includes(":")) {
    return { version: connectorCdkVersion, isLatest: false };
  }

  const [language, version] = connectorCdkVersion.split(":");
  switch (language) {
    case "python":
      const isLatest = version === latestPythonCdkVersion;
      const packageUrl = `https://pypi.org/project/airbyte-cdk/${version}/`;
      return { version, isLatest, url: packageUrl };
    case "java":
      return { version, isLatest: version === latestJavaCdkVersion, url: null };
    default:
      return { version, isLatest: false, url: null };
  }
};

function getSupportLevelDisplay(rawSupportLevel) {
  switch (rawSupportLevel) {
    case "certified":
      return "Airbyte";
    case "community":
      return "Marketplace";
    case "enterprise":
      return "Enterprise";
    case "archived":
      return "Archived";
    default:
      return null;
  }
}

module.exports = {
  isPypiConnector: (connector) => {
    return Boolean(connector.remoteRegistries_oss?.pypi?.enabled);
  },
  getLatestPythonCDKVersion,
  parseCDKVersion,
  getSupportLevelDisplay,
};
