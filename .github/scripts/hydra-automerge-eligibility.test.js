const assert = require("node:assert/strict");
const test = require("node:test");

const {
  autoMergePreconditionsPass,
  classifyAutoMergeEligibility,
} = require("./hydra-automerge-eligibility");

const sourceFile = {
  filename: "airbyte-integrations/connectors/source-faker/metadata.yaml",
};
const supportBot = { login: "airbyte-support-bot" };

test("allows an assigned source PR through deterministic eligibility", () => {
  const eligibility = classifyAutoMergeEligibility([sourceFile], [supportBot]);

  assert.equal(eligibility.valid, true);
  assert.equal(eligibility.supportBotAssigned, true);
  assert.equal(eligibility.noDestinationChanges, true);
});

test("rejects a source PR without the Support Bot assignment", () => {
  const eligibility = classifyAutoMergeEligibility([sourceFile], []);

  assert.equal(eligibility.valid, true);
  assert.equal(eligibility.supportBotAssigned, false);
  assert.equal(eligibility.noDestinationChanges, true);
});

test("rejects destination connector and documentation changes", () => {
  const eligibility = classifyAutoMergeEligibility(
    [
      {
        filename:
          "airbyte-integrations/connectors/destination-postgres/metadata.yaml",
      },
      { filename: "docs/integrations/destinations/postgres.md" },
    ],
    [supportBot],
  );

  assert.equal(eligibility.valid, true);
  assert.equal(eligibility.supportBotAssigned, true);
  assert.equal(eligibility.noDestinationChanges, false);
});

test("rejects a rename from a destination connector path", () => {
  const eligibility = classifyAutoMergeEligibility(
    [
      {
        filename: "airbyte-integrations/connectors/source-faker/metadata.yaml",
        previous_filename:
          "airbyte-integrations/connectors/destination-faker/metadata.yaml",
      },
    ],
    [supportBot],
  );

  assert.equal(eligibility.noDestinationChanges, false);
});

test("preserves connector-only path validation", () => {
  const eligibility = classifyAutoMergeEligibility(
    [{ filename: "airbyte-api/server/src/main/kotlin/Application.kt" }],
    [supportBot],
  );

  assert.equal(eligibility.valid, false);
  assert.equal(
    eligibility.invalidPath,
    "airbyte-api/server/src/main/kotlin/Application.kt",
  );
});

test("requires assignment and no destination changes in every combination", () => {
  for (const supportBotAssigned of [true, false]) {
    for (const noDestinationChanges of [true, false]) {
      const result = autoMergePreconditionsPass({
        aiReviewPassed: true,
        noBreakingChanges: true,
        noDestinationChanges,
        supportBotAssigned,
      });

      assert.equal(
        result,
        supportBotAssigned && noDestinationChanges,
        `assignment=${supportBotAssigned}, noDestinationChanges=${noDestinationChanges}`,
      );
    }
  }
});

test("preserves existing AI-review and breaking-change prerequisites", () => {
  assert.equal(
    autoMergePreconditionsPass({
      aiReviewPassed: false,
      noBreakingChanges: true,
      noDestinationChanges: true,
      supportBotAssigned: true,
    }),
    false,
  );
  assert.equal(
    autoMergePreconditionsPass({
      aiReviewPassed: true,
      noBreakingChanges: false,
      noDestinationChanges: true,
      supportBotAssigned: true,
    }),
    false,
  );
});
