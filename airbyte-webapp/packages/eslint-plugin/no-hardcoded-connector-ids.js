const destinations = require("../../src/utils/connectors/destinations.json");
const sources = require("../../src/utils/connectors/sources.json");

// Create a map for connector id to variable name (i.e. flip the direction of the map)
const sourceIdToName = Object.fromEntries(Object.entries(sources).map((entry) => [entry[1], entry[0]]));
const destinationIdToName = Object.fromEntries(Object.entries(destinations).map((entry) => [entry[1], entry[0]]));

const validateStringContent = (context, node, nodeContent) => {
  if (nodeContent in destinationIdToName) {
    context.report({ node, messageId: "destinationId", data: { id: nodeContent, name: destinationIdToName[nodeContent] } });
  } else if (nodeContent in sourceIdToName) {
    context.report({ node, messageId: "sourceId", data: { id: nodeContent, name: sourceIdToName[nodeContent] } });
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
