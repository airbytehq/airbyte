const destinations = require("../../src/utils/connectors/destinations.json");
const sources = require("../../src/utils/connectors/sources.json");

// Create a map for connector id to variable name (i.e. flip the direction of the map)
const sourceIds = Object.fromEntries(Object.entries(sources).map((entry) => [entry[1], entry[0]]));
const destinationIds = Object.fromEntries(Object.entries(destinations).map((entry) => [entry[1], entry[0]]));

const validateStringContent = (context, node, string) => {
  if (string in destinationIds) {
    context.report({ node, messageId: "destinationId", data: { id: string, name: destinationIds[string] } });
  } else if (string in sourceIds) {
    context.report({ node, messageId: "sourceId", data: { id: string, name: sourceIds[string] } });
  }
};

module.exports = {
  meta: {
    type: "suggestion",
    messages: {
      sourceId: "Found hard-coded connector id, use `ConnectorIds.Sources.{{ name }}` from `utils/connectors` instead.",
      destinationId:
        "Found hard-coded connector id, use `ConnectorIds.Destinations.{{ name }}` from `utils/connectors` instead.",
    },
  },
  create: (context) => ({
    Literal: (node) => {
      if (typeof node.value === "string") {
        validateStringContent(context, node, node.value);
      }
    },
    TemplateLiteral: (node) => {
      // Only check template literals which are "static", i.e. don't contain ${} elements
      if (!node.expressions.length && node.quasis.length === 1) {
        validateStringContent(context, node, node.quasis[0].value.raw);
      }
    },
  }),
};
