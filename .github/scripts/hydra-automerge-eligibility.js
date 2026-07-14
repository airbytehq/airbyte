const ALLOWED_PATHS = [
  /^airbyte-integrations\/connectors\//,
  /^docs\/integrations\/sources\//,
  /^docs\/integrations\/destinations\//,
  /^docs\/ai-agents\/connectors\//,
  /^docs\/developers\/pyairbyte\//,
  /^docs\/release_notes\//,
  /^docusaurus\/src\/data\//,
];

function classifyAutoMergeEligibility(files, assignees) {
  const invalidPath = files
    .map((file) => file.filename)
    .find((path) => !ALLOWED_PATHS.some((pattern) => pattern.test(path)));
  const changedPaths = files.flatMap((file) =>
    [file.filename, file.previous_filename].filter(Boolean),
  );
  const destinationChanges = changedPaths.some(
    (path) =>
      /^airbyte-integrations\/connectors\/destination-[^/]+\//.test(path) ||
      /^docs\/integrations\/destinations\//.test(path),
  );
  const supportBotAssigned = assignees.some(
    (assignee) => assignee.login === "airbyte-support-bot",
  );

  return {
    destinationReasoning: destinationChanges
      ? "Destination-related changes require human approval and merge."
      : "No destination-related changes detected.",
    invalidPath,
    noDestinationChanges: !destinationChanges,
    supportBotAssigned,
    supportBotReasoning: supportBotAssigned
      ? "Airbyte Support Bot assignment confirms automated merge eligibility."
      : "Airbyte Support Bot is not assigned; human approval and merge are required.",
    valid: !invalidPath,
  };
}

function autoMergePreconditionsPass({
  aiReviewPassed,
  noBreakingChanges,
  noDestinationChanges,
  supportBotAssigned,
}) {
  return [
    aiReviewPassed,
    noBreakingChanges,
    noDestinationChanges,
    supportBotAssigned,
  ].every((value) => value === true || value === "true");
}

module.exports = {
  autoMergePreconditionsPass,
  classifyAutoMergeEligibility,
};
