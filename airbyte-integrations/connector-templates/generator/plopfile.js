"use strict";
const path = require("path");
const uuid = require("uuid");
const capitalCase = require("capital-case");
const changeCase = require("change-case");
const getSuccessMessage = function (
  connectorName,
  outputPath,
  additionalMessage
) {
  return `
🚀 🚀 🚀 🚀 🚀 🚀

Success!

Your ${connectorName} connector has been created at .${path.resolve(
  outputPath
)}.

Follow the TODOs in the generated module to implement your connector.

Questions, comments, or concerns? Let us know in our connector development forum:
https://discuss.airbyte.io/c/connector-development/16

We're always happy to provide any support!

${additionalMessage || ""}
`;
};

module.exports = function (plop) {
  const connectorAcceptanceTestFilesInputRoot =
    "../connector_acceptance_test_files";

  const pythonSourceInputRoot = "../source-python";
  const pythonDestinationInputRoot = "../destination-python";

  const outputDir = "../../connectors";

  const pythonSourceOutputRoot = `${outputDir}/source-{{dashCase name}}`;
  const pythonDestinationOutputRoot = `${outputDir}/destination-{{dashCase name}}`;

  const sourceConnectorImagePrefix = "airbyte/source-";
  const sourceConnectorImageTag = "dev";
  const defaultSpecPathFolderPrefix = "source_";

  const specFileName = "spec.yaml";

  plop.setHelper("capitalCase", function (name) {
    return capitalCase.capitalCase(name);
  });

  plop.setHelper("currentYear", function () {
    return new Date().getFullYear();
  });

  plop.setHelper("generateDefinitionId", function () {
    // if the env var CI is set then return a fixed FAKE uuid  so that the tests are deterministic
    if (process.env.CI) {
      return "FAKE-UUID-0000-0000-000000000000";
    }
    return uuid.v4().toLowerCase();
  });

  plop.setHelper("connectorImage", function () {
    let suffix = "";
    if (typeof this.connectorImageNameSuffix !== "undefined") {
      suffix = this.connectorImageNameSuffix;
    }
    return `${sourceConnectorImagePrefix}${changeCase.paramCase(this.name)}${suffix}:${sourceConnectorImageTag}`;
  });

  plop.setHelper("specPath", function () {
    let suffix = "";
    if (typeof this.specPathFolderSuffix !== "undefined") {
      suffix = this.specPathFolderSuffix;
    }
    let inSubFolder = true;
    if (typeof this.inSubFolder !== "undefined") {
      inSubFolder = this.inSubFolder;
    }
    if (inSubFolder) {
      return `${defaultSpecPathFolderPrefix}${changeCase.snakeCase(
        this.name
      )}${suffix}/${specFileName}`;
    } else {
      return specFileName;
    }
  });

  plop.setActionType("emitSuccess", function (answers, config, plopApi) {
    console.log(
      getSuccessMessage(
        answers.name,
        plopApi.renderString(config.outputPath, answers),
        config.message
      )
    );
  });

  plop.setGenerator("Python CDK Destination", {
    description: "Generate a destination connector based on Python CDK.",
    prompts: [
      { type: "input", name: "name", message: "Connector name e.g: redis" },
    ],
    actions: [
      {
        abortOnFail: true,
        type: "addMany",
        destination: pythonDestinationOutputRoot,
        base: pythonDestinationInputRoot,
        templateFiles: `${pythonDestinationInputRoot}/**/**`,
      },
      { type: "emitSuccess", outputPath: pythonDestinationOutputRoot },
    ],
  });

  plop.setGenerator("Python CDK Source", {
    description:
      "Generate a source connector based on Python CDK.",
    prompts: [
      {
        type: "input",
        name: "name",
        message: 'Source name e.g: "google-analytics"',
      },
    ],
    actions: [
      {
        abortOnFail: true,
        type: "addMany",
        destination: pythonSourceOutputRoot,
        base: pythonSourceInputRoot,
        templateFiles: `${pythonSourceInputRoot}/**/**`,
      },
      // common acceptance tests
      {
        abortOnFail: true,
        type: "addMany",
        destination: pythonSourceOutputRoot,
        base: connectorAcceptanceTestFilesInputRoot,
        templateFiles: `${connectorAcceptanceTestFilesInputRoot}/**/**`,
      },
      { type: "emitSuccess", outputPath: pythonSourceOutputRoot },
    ],
  });

};
