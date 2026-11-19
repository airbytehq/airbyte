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

test("fork restriction appends to the original comment", () => {
  const step = dispatcher
    .split("- name: Explain fork PR restriction\n")[1]
    .split("\n      - name:")[0];
  assert.match(
    step,
    /uses: peter-evans\/create-or-update-comment@a35cf36e5301d70b76f316e867e7788a55a31dae/,
  );
  assert.match(step, /edit-mode: append/);
  assert.match(step, /comment-id: \$\{\{ github.event.comment.id \}\}/);
  assert.doesNotMatch(step, /run:/);
});

function dependencies(workflow) {
  const jobs = workflow.split("\njobs:\n")[1];
  assert.ok(jobs, "Workflow must declare jobs");
  const headings = [...jobs.matchAll(/^  ([\w-]+):\n/gm)];
  return Object.fromEntries(
    headings.map((heading, index) => {
      const body = jobs.slice(heading.index, headings[index + 1]?.index);
      const needs = body.match(
        /^    needs:([^\n]*)(?:\n((?:      - [\w-]+\n)+))?/m,
      );
      const names = needs
        ? (needs[1] + (needs[2] || "")).match(/[a-zA-Z_][\w-]*/g) || []
        : [];
      return [heading[1], names];
    }),
  );
}

function assertGuarded(graph) {
  const roots = Object.keys(graph).filter((job) => graph[job].length === 0);
  assert.deepEqual(roots, ["guard-pr"]);
  function reachesGuard(job, visited = new Set()) {
    assert.ok(Object.hasOwn(graph, job), "Unknown dependency: " + job);
    assert.ok(!visited.has(job), "Cyclic dependency: " + job);
    return (
      job === "guard-pr" ||
      graph[job].some((dependency) =>
        reachesGuard(dependency, new Set([...visited, job])),
      )
    );
  }
  for (const job of Object.keys(graph)) {
    assert.ok(reachesGuard(job), job + " must depend on guard-pr");
  }
  return roots;
}

test("dependency checks reject a parallel unguarded job", () => {
  assert.throws(() =>
    assertGuarded({
      "guard-pr": [],
      protected: ["guard-pr"],
      parallel: [],
    }),
  );
});

test("all jobs in blocked entry workflows depend on the only root, guard-pr", () => {
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
    const roots = assertGuarded(dependencies(workflow));
    console.log(command + "-command.yml root jobs: " + roots.join(", "));
    const guardJob = workflow.split("\njobs:\n")[1].split(/\n  [\w-]+:\n/)[0];
    assert.doesNotMatch(guardJob, /secrets:/);
  }
});
