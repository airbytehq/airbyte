#! /usr/bin/env ts-node

import fetch from "node-fetch";

import { links } from "../src/utils/links";

async function run() {
  // Query all domains and wait for results
  const results = await Promise.allSettled(
    Object.entries(links).map(([key, url]) => {
      return fetch(url, { headers: { "user-agent": "ValidateLinksCheck" } })
        .then((resp) => {
          if (resp.status >= 200 && resp.status < 300) {
            // Only URLs returning a 200 status code are considered okay
            console.log(`✓ [${key}] ${url} returned HTTP ${resp.status}`);
          } else {
            // Everything else should fail this test
            console.error(`X [${key}] ${url} returned HTTP ${resp.status}`);
            return Promise.reject({ key, url });
          }
        })
        .catch((reason) => {
          console.error(`X [${key}] ${url} error fetching: ${String(reason)}`);
          return Promise.reject({ key, url });
        });
    })
  );

  const failures = results.filter((result): result is PromiseRejectedResult => result.status === "rejected");

  if (failures.length > 0) {
    console.log(`\nThe following URLs were not successful: ${failures.map((r) => r.reason.key).join(", ")}`);
    process.exit(1);
  } else {
    console.log("\n✓ All URLs have been checked successfully.");
  }
}

run();
