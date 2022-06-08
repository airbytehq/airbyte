const path = require("path");
const { promisify } = require("util");

const checker = require("license-checker");

const { version } = require("../package.json");

/**
 * A list of all the allowed licenses that production dependencies can have.
 */
const ALLOWED_LICENSES = [
  "(Apache-2.0 OR MPL-1.1)",
  "(AFL-2.1 OR BSD-3-Clause)",
  "(AFLv2.1 OR BSD)",
  "(BSD-2-Clause OR MIT OR Apache-2.0)",
  "(BSD-3-Clause AND Apache-2.0)",
  "(BSD-3-Clause OR GPL-2.0)",
  "(CC-BY-4.0 AND MIT)",
  "(MIT OR Apache-2.0)",
  "(MIT OR CC0-1.0)",
  "(MIT OR GPL-3.0)",
  "(MIT OR GPL-3.0-or-later)",
  "(MIT OR WTFPL)",
  "(MIT AND CC-BY-3.0)",
  "(MIT AND BSD-3-Clause)",
  "(MIT AND Zlib)",
  "(WTFPL OR MIT)",
  "BSD-3-Clause OR MIT",
  "0BSD",
  "Apache",
  "Apache-2.0",
  "BSD",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "CC0-1.0",
  "CC-BY-3.0",
  "CC-BY-4.0",
  "ISC",
  "MIT",
  "MPL-2.0",
  "Public Domain",
  "Python-2.0",
  "Unlicense",
  "WTFPL",
];

/**
 * Licenses that should be allowed only for dev dependencies.
 */
const ALLOWED_DEV_LICENSES = [...ALLOWED_LICENSES, "ODC-By-1.0", "MPL-2.0"];

/**
 * A list of all packages that should be excluded from license checking.
 */
const IGNORED_PACKAGES = [`airbyte-webapp@${version}`];

/**
 * Overwrite licenses for specific packages manually, e.g. because they can't be detected properly.
 */
const LICENSE_OVERWRITES = {
  "glob-to-regexp@0.3.0": "BSD-3-Clause",
  "trim@0.0.1": "MIT",
  "backslash@0.2.0": "MIT",
  "browser-assert@1.2.1": "MIT", // via README (https://github.com/socialally/browser-assert/tree/v1.2.1)
};

const checkLicenses = promisify(checker.init);
const params = {
  start: path.join(__dirname, ".."),
  excludePackages: IGNORED_PACKAGES.join(";"),
  unknown: true,
};

function validateLicenes(licenses, allowedLicenes, usedOverwrites) {
  let licensesValid = true;
  for (const [pkg, info] of Object.entries(licenses)) {
    let license = Array.isArray(info.licenses) ? `(${info.licenses.join(" OR ")})` : info.licenses;
    if (LICENSE_OVERWRITES[pkg]) {
      license = LICENSE_OVERWRITES[pkg];
      usedOverwrites.add(pkg);
    }
    if (license.endsWith("*")) {
      license = license.substr(0, license.length - 1);
      console.log(`Guessed license for package ${pkg}: ${license}`);
    }
    if (!license || !allowedLicenes.includes(license)) {
      licensesValid = false;
      console.error(`Package ${pkg} has incompatible license: ${license}`);
    }
  }

  return licensesValid;
}

Promise.all([checkLicenses({ ...params, production: true }), checkLicenses({ ...params, development: true })]).then(
  ([prod, dev]) => {
    const usedOverwrites = new Set();
    const prodLicensesValid = validateLicenes(prod, ALLOWED_LICENSES, usedOverwrites);
    const devLicensesValid = validateLicenes(dev, ALLOWED_DEV_LICENSES, usedOverwrites);

    for (const overwrite of Object.keys(LICENSE_OVERWRITES)) {
      if (!usedOverwrites.has(overwrite)) {
        console.warn(`License overwrite for ${overwrite} is no longer needed and can be deleted.`);
      }
    }

    if (!prodLicensesValid || !devLicensesValid) {
      process.exit(1);
    }
  }
);
