const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { test } = require("node:test");

const workflows = path.resolve(__dirname, "../../workflows");
const dispatcher = fs.readFileSync(
  path.join(workflows, "slash-commands.yml"),
  "utf8",
);
const guard = fs.readFileSync(
  path.join(workflows, "guard-command-pr.yml"),
  "utf8",
);
const blocked = [
  "build-connector-images",
  "bump-progressive-rollout-version",
  "bump-version",
  "enable-autopilot-rollouts",
  "format-fix",
  "poe",
  "publish-connectors-prerelease",
  "publish-java-cdk",
  "run-connector-tests",
];

function script(workflow, stepName) {
  const step = workflow.split("- name: " + stepName + "\n")[1];
  assert.ok(step, stepName);
  return step
    .split("        run: |\n")[1]
    .match(/^(?:          .*\n|\n)+/)[0]
    .replace(/^          /gm, "");
}

function run(script, env = {}, prelude = "") {
  return spawnSync(
    "bash",
    ["-euo", "pipefail", "-c", prelude + "\n" + script],
    {
      encoding: "utf8",
      env: {
        ...process.env,
        GITHUB_REPOSITORY: "airbytehq/airbyte",
        GITHUB_OUTPUT: "/dev/null",
        ...env,
      },
    },
  );
}

test("fork dispatcher blocks every privileged command, including whitespace and arguments", () => {
  for (const command of blocked) {
    for (const body of [
      "/" + command,
      "/" + command + " connector=x\r\ntext",
      "/\t" + command,
    ]) {
      const result = run(script(dispatcher, "Resolve fork command policy"), {
        COMMENT_BODY: body,
        IS_FORK: "true",
      });
      assert.equal(result.status, 0, result.stderr);
      assert.match(result.stdout, /blocked=true/);
    }
  }
  assert.match(dispatcher, /if: steps.fork-policy.outputs.blocked != 'true'/);
  assert.match(dispatcher, /if: steps.fork-policy.outputs.blocked == 'true'/);
});

test("same-repo, issue, empty and remote AI commands are not blocked", () => {
  for (const [body, fork] of [
    ["/poe", "false"],
    ["/poe", ""],
    ["", "true"],
    ["/unknown", "true"],
    ...dispatcher
      .match(/            ai-[\w-]+/g)
      .map((command) => ["/" + command.trim(), "true"]),
  ]) {
    const result = run(script(dispatcher, "Resolve fork command policy"), {
      COMMENT_BODY: body,
      IS_FORK: fork,
    });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /blocked=false/);
  }
});

test("guard rejects external repo before PR lookup or checkout", () => {
  assert.match(
    guard,
    /if: inputs.repo != '' && inputs.repo != github.repository/,
  );
  const result = run(script(guard, "Reject an external repository"));
  assert.equal(result.status, 1);
  assert.match(result.stdout, /Fork PRs cannot run this command/);
  assert.doesNotMatch(guard, /actions\/checkout|secrets:/);
  assert.match(guard, /GH_TOKEN: \$\{\{ github.token \}\}/);
});

test("PR validation accepts same repo and rejects forks, deleted heads and API failures", () => {
  const validate = script(guard, "Validate PR head repository");
  for (const [head, status] of [
    ["airbytehq/airbyte", 0],
    ["contributor/airbyte", 1],
    ["null", 1],
    ["", 1],
  ]) {
    const result = run(
      validate,
      { PR_NUMBER: "123", HEAD: head },
      'gh() { printf "%s\\n" "$HEAD"; }',
    );
    assert.equal(result.status, status, result.stderr);
  }
  assert.notEqual(
    run(validate, { PR_NUMBER: "123" }, "gh() { return 1; }").status,
    0,
  );
  for (const pr of ["0", "-1", "abc", "1/../../", "$(exit 0)"]) {
    const result = run(
      validate,
      { PR_NUMBER: pr },
      'gh() { echo "unexpected API call" >&2; return 99; }',
    );
    assert.equal(result.status, 1);
    assert.doesNotMatch(result.stderr, /unexpected API call/);
  }
  assert.match(guard, /if: inputs.pr != ''/);
});

test("all blocked entry workflows gate their root job without inheriting secrets", () => {
  for (const command of blocked) {
    const workflow = fs.readFileSync(
      path.join(workflows, command + "-command.yml"),
      "utf8",
    );
    assert.match(
      workflow,
      /jobs:\n  guard-pr:\n    name: Reject fork PRs\n    uses: \.\/\.github\/workflows\/guard-command-pr.yml/,
    );
    assert.match(
      workflow,
      /pr: \$\{\{ inputs.pr && format\('\{0\}', inputs.pr\) \|\| '' \}\}/,
    );
    assert.match(workflow, /repo: \$\{\{ inputs.repo \|\| '' \}\}/);
    const jobs = workflow.split("\njobs:\n")[1];
    const firstJob = jobs.split(/\n  [\w-]+:\n/)[1];
    assert.match(firstJob, /    needs: guard-pr/);
    assert.doesNotMatch(jobs.split(/\n  [\w-]+:\n/)[0], /secrets:/);
  }
});
