export const noPredicateAdvancedAuth = {
  authFlowType: "oauth2.0" as const,
  predicateKey: [],
  predicateValue: "",
  oauthConfigSpecification: {
    completeOAuthOutputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {
        access_token: {
          type: "string",
          path_in_connector_config: ["access_token"],
        },
      },
    },
    completeOAuthServerInputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {
        client_id: {
          type: "string",
        },
        client_secret: {
          type: "string",
        },
      },
    },
    completeOAuthServerOutputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {},
    },
  },
};

export const predicateInsideConditional = {
  authFlowType: "oauth2.0" as const,
  predicateKey: ["credentials", "auth_type"],
  predicateValue: "oauth2.0",
  oauthConfigSpecification: {
    completeOAuthOutputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {
        access_token: {
          type: "string",
          path_in_connector_config: ["credentials", "access_token"],
        },
      },
    },
    completeOAuthServerInputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {
        client_id: {
          type: "string",
        },
        client_secret: {
          type: "string",
        },
      },
    },
    completeOAuthServerOutputSpecification: {
      type: "object",
      additionalProperties: false,
      properties: {
        client_id: {
          type: "string",
          path_in_connector_config: ["credentials", "client_id"],
        },
        client_secret: {
          type: "string",
          path_in_connector_config: ["credentials", "client_secret"],
        },
      },
    },
  },
};
