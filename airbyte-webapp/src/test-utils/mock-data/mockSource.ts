import { SourceDefinitionRead, SourceDefinitionSpecificationRead } from "core/request/AirbyteClient";

import { ConnectorIds } from "../../utils/connectors";

export const mockSourceDefinition: SourceDefinitionRead = {
  sourceDefinitionId: ConnectorIds.Sources.Postgres,
  name: "Postgres",
  dockerRepository: "airbyte/source-postgres",
  dockerImageTag: "1.0.39",
  documentationUrl: "https://docs.airbyte.com/integrations/sources/postgres",
  icon: '<svg xmlns="http://www.w3.org/2000/svg" width="250" height="250" fill="none"><g clip-path="url(#a)"><path fill="#000" d="M219.262 144.355c-1.14-3.451-4.124-5.855-7.983-6.432-1.82-.271-3.904-.156-6.37.353-4.299.887-7.488 1.225-9.816 1.29 8.785-14.836 15.929-31.754 20.041-47.68 6.65-25.751 3.097-37.482-1.056-42.789-10.989-14.045-27.023-21.59-46.366-21.821-10.318-.126-19.377 1.912-24.102 3.377-4.4-.777-9.131-1.21-14.094-1.29-9.305-.149-17.526 1.88-24.551 6.05-3.889-1.316-10.13-3.17-17.339-4.353-16.953-2.784-30.617-.615-40.611 6.447-12.102 8.55-17.712 23.406-16.675 44.155.33 6.588 4.014 26.631 9.815 45.64 3.334 10.926 6.889 19.999 10.566 26.969 5.216 9.885 10.796 15.705 17.061 17.796 3.511 1.17 9.891 1.989 16.601-3.601.85 1.031 1.986 2.055 3.492 3.006 1.912 1.206 4.25 2.192 6.587 2.776 8.417 2.104 16.301 1.578 23.027-1.372.042 1.197.074 2.34.101 3.327.044 1.602.089 3.172.147 4.64.399 9.928 1.074 17.648 3.075 23.049.11.297.258.75.413 1.23.999 3.057 2.668 8.175 6.915 12.183 4.397 4.152 9.716 5.425 14.588 5.425 2.443 0 4.775-.321 6.819-.759 7.289-1.562 15.566-3.942 21.554-12.47 5.662-8.062 8.414-20.205 8.912-39.338l.181-1.55.118-1.011 1.334.118.344.023c7.423.338 16.5-1.236 22.075-3.826 4.405-2.045 18.52-9.499 15.197-19.562"/><path fill="#336791" d="M206.57 146.312c-22.073 4.554-23.591-2.92-23.591-2.92 23.305-34.589 33.048-78.493 24.641-89.239-22.937-29.312-62.64-15.449-63.303-15.09l-.213.039c-4.361-.906-9.241-1.445-14.726-1.535-9.987-.163-17.563 2.62-23.312 6.98 0 0-70.827-29.185-67.533 36.705.701 14.017 20.087 106.062 43.209 78.26 8.451-10.167 16.618-18.762 16.618-18.762 4.055 2.694 8.91 4.069 14 3.576l.396-.336c-.123 1.262-.067 2.496.158 3.958-5.957 6.657-4.206 7.825-16.114 10.277-12.05 2.484-4.97 6.906-.35 8.062 5.603 1.401 18.565 3.386 27.323-8.877l-.349 1.4c2.333 1.869 3.972 12.161 3.698 21.492-.275 9.33-.458 15.736 1.38 20.739 1.84 5.004 3.672 16.261 19.327 12.907 13.079-2.804 19.858-10.07 20.801-22.189.669-8.616 2.183-7.342 2.278-15.045l1.215-3.647c1.401-11.679.223-15.447 8.281-13.695l1.959.172c5.93.27 13.694-.954 18.25-3.072 9.81-4.554 15.629-12.158 5.955-10.16h.002"/><path fill="#fff" d="M110.212 87.52c-1.989-.277-3.791-.02-4.702.67-.512.388-.671.838-.714 1.148-.114.82.46 1.727.813 2.195.999 1.324 2.459 2.234 3.903 2.435.209.03.418.043.625.043 2.408 0 4.598-1.876 4.791-3.26.242-1.735-2.275-2.89-4.716-3.23Zm65.894.055c-.19-1.359-2.608-1.746-4.903-1.427-2.292.319-4.514 1.354-4.328 2.716.148 1.06 2.061 2.868 4.325 2.868.191 0 .384-.013.578-.04 1.512-.21 2.62-1.17 3.147-1.723.802-.843 1.267-1.783 1.181-2.394"/><path fill="#fff" d="M213.915 145.795c-.841-2.546-3.55-3.365-8.051-2.435-13.363 2.758-18.149.848-19.72-.31 10.387-15.827 18.932-34.958 23.542-52.808 2.183-8.456 3.389-16.308 3.488-22.709.109-7.025-1.087-12.187-3.554-15.34-9.947-12.713-24.546-19.532-42.218-19.72-12.148-.136-22.413 2.974-24.403 3.848-4.19-1.042-8.758-1.682-13.732-1.764-9.12-.147-17.003 2.037-23.53 6.488-2.835-1.055-10.162-3.57-19.123-5.015-15.49-2.494-27.8-.604-36.585 5.62-10.482 7.428-15.321 20.706-14.384 39.464.316 6.31 3.911 25.725 9.584 44.317 7.468 24.47 15.586 38.323 24.127 41.173 1 .334 2.153.567 3.424.567 3.116 0 6.936-1.405 10.91-6.184a393.103 393.103 0 0 1 15.038-17.019c3.357 1.802 7.046 2.809 10.819 2.91.007.099.017.197.026.295a87.647 87.647 0 0 0-1.908 2.357c-2.614 3.319-3.158 4.01-11.572 5.743-2.394.495-8.75 1.805-8.844 6.262-.1 4.87 7.515 6.915 8.382 7.132 3.024.757 5.937 1.13 8.715 1.13 6.756 0 12.702-2.221 17.453-6.518-.146 17.36.578 34.467 2.662 39.679 1.707 4.267 5.877 14.695 19.047 14.694 1.933 0 4.06-.225 6.4-.727 13.746-2.947 19.716-9.024 22.025-22.421 1.235-7.16 3.356-24.257 4.353-33.428 2.105.657 4.815.958 7.744.957 6.11 0 13.16-1.298 17.581-3.351 4.967-2.307 13.93-7.968 12.304-12.887ZM181.18 83.823c-.045 2.708-.417 5.166-.812 7.731-.426 2.76-.865 5.612-.976 9.075-.109 3.371.312 6.875.719 10.263.822 6.845 1.666 13.891-1.6 20.844a27.06 27.06 0 0 1-1.448-2.976c-.406-.984-1.287-2.565-2.508-4.754-4.749-8.519-15.871-28.469-10.178-36.61 1.696-2.423 6-4.914 16.803-3.573Zm-13.095-45.867c15.834.35 28.359 6.274 37.227 17.608 6.801 8.694-.688 48.252-22.37 82.378-.218-.277-.437-.553-.657-.829l-.275-.343c5.603-9.255 4.507-18.412 3.532-26.53-.401-3.332-.779-6.479-.683-9.435.1-3.132.514-5.82.915-8.418.492-3.202.993-6.515.855-10.42.103-.41.145-.894.09-1.469-.352-3.745-4.627-14.953-13.341-25.098-4.766-5.55-11.716-11.76-21.207-15.948 4.082-.846 9.664-1.635 15.914-1.496Zm-88.6 119.533c-4.38 5.266-7.403 4.257-8.398 3.926-6.48-2.162-13.998-15.86-20.626-37.581-5.736-18.795-9.087-37.694-9.353-42.994-.837-16.76 3.225-28.442 12.074-34.719 14.401-10.215 38.078-4.1 47.593-1-.137.135-.279.261-.414.399-15.613 15.77-15.243 42.714-15.204 44.362-.002.635.052 1.535.124 2.772.27 4.532.77 12.967-.567 22.519-1.24 8.876 1.495 17.564 7.505 23.836a26.998 26.998 0 0 0 1.942 1.832 401.89 401.89 0 0 0-14.677 16.648Zm16.683-22.265c-4.844-5.056-7.044-12.087-6.036-19.294 1.41-10.09.89-18.878.61-23.6-.04-.66-.075-1.239-.095-1.695 2.281-2.023 12.851-7.688 20.388-5.96 3.44.788 5.536 3.13 6.407 7.16 4.51 20.862.597 29.557-2.547 36.545-.648 1.439-1.26 2.8-1.783 4.208l-.405 1.088c-1.026 2.751-1.98 5.309-2.572 7.738-5.149-.015-10.158-2.215-13.967-6.191v.001Zm.79 28.135c-1.503-.376-2.856-1.028-3.649-1.57.663-.311 1.842-.736 3.888-1.158 9.898-2.037 11.427-3.476 14.765-7.716.766-.972 1.633-2.074 2.835-3.416l.001-.001c1.79-2.005 2.608-1.665 4.093-1.049 1.203.498 2.375 2.006 2.85 3.666.225.784.477 2.272-.349 3.43-6.974 9.766-17.136 9.641-24.434 7.814Zm51.804 48.217c-12.109 2.595-16.397-3.585-19.222-10.65-1.824-4.561-2.72-25.128-2.084-47.842a2.75 2.75 0 0 0-.118-.869 11.595 11.595 0 0 0-.339-1.605c-.945-3.305-3.25-6.069-6.015-7.215-1.098-.455-3.114-1.29-5.536-.671.516-2.129 1.412-4.533 2.384-7.137l.407-1.094c.459-1.235 1.035-2.514 1.643-3.868 3.29-7.311 7.796-17.324 2.906-39.946-1.832-8.473-7.949-12.611-17.222-11.65-5.559.576-10.645 2.819-13.182 4.106a42.56 42.56 0 0 0-1.51.803c.708-8.537 3.383-24.492 13.389-34.586 6.3-6.355 14.691-9.493 24.914-9.324 20.143.33 33.06 10.669 40.35 19.285 6.281 7.424 9.683 14.904 11.04 18.938-10.208-1.039-17.152.977-20.671 6.01-7.657 10.948 4.189 32.197 9.882 42.409 1.044 1.872 1.945 3.489 2.229 4.177 1.854 4.494 4.254 7.495 6.006 9.685.538.671 1.059 1.322 1.455 1.89-3.092.892-8.646 2.952-8.139 13.249-.409 5.167-3.311 29.357-4.786 37.904-1.947 11.291-6.101 15.496-17.781 18.002v-.001Zm50.546-57.856c-3.161 1.468-8.452 2.569-13.479 2.805-5.551.26-8.377-.622-9.042-1.164-.312-6.417 2.076-7.087 4.603-7.797.397-.112.784-.221 1.158-.351.233.189.487.377.766.561 4.462 2.946 12.421 3.263 23.657.943l.123-.024c-1.516 1.417-4.109 3.319-7.786 5.027Z"/></g><defs><clipPath id="a"><path fill="#fff" d="M30 27h190v196H30z"/></clipPath></defs></svg>',
  protocolVersion: "0.2.0",
  releaseStage: "generally_available",
  sourceType: "database",
};

export const mockSourceDefinitionSpecification: SourceDefinitionSpecificationRead = {
  sourceDefinitionId: ConnectorIds.Sources.Postgres,
  documentationUrl: "https://docs.airbyte.com/integrations/sources/postgres",
  connectionSpecification: {
    type: "object",
    title: "Postgres Source Spec",
    $schema: "http://json-schema.org/draft-07/schema#",
    required: ["host", "port", "database", "username"],
    properties: {
      ssl: {
        type: "boolean",
        order: 7,
        title: "Connect using SSL",
        default: false,
        description: "Encrypt data using SSL. When activating SSL, please select one of the connection modes.",
      },
      host: {
        type: "string",
        order: 0,
        title: "Host",
        description: "Hostname of the database.",
      },
      port: {
        type: "integer",
        order: 1,
        title: "Port",
        default: 5432,
        maximum: 65536,
        minimum: 0,
        examples: ["5432"],
        description: "Port of the database.",
      },
      schemas: {
        type: "array",
        items: {
          type: "string",
        },
        order: 3,
        title: "Schemas",
        default: ["public"],
        minItems: 0,
        description: "The list of schemas (case sensitive) to sync from. Defaults to public.",
        uniqueItems: true,
      },
      database: {
        type: "string",
        order: 2,
        title: "Database Name",
        description: "Name of the database.",
      },
      password: {
        type: "string",
        order: 5,
        title: "Password",
        description: "Password associated with the username.",
        airbyte_secret: true,
      },
      ssl_mode: {
        type: "object",
        oneOf: [
          {
            title: "disable",
            required: ["mode"],
            properties: {
              mode: {
                type: "string",
                const: "disable",
                order: 0,
              },
            },
            description: "Disables encryption of communication between Airbyte and source database.",
            additionalProperties: true,
          },
          {
            title: "allow",
            required: ["mode"],
            properties: {
              mode: {
                type: "string",
                const: "allow",
                order: 0,
              },
            },
            description: "Enables encryption only when required by the source database.",
            additionalProperties: true,
          },
          {
            title: "prefer",
            required: ["mode"],
            properties: {
              mode: {
                type: "string",
                const: "prefer",
                order: 0,
              },
            },
            description: "Allows unencrypted connection only if the source database does not support encryption.",
            additionalProperties: true,
          },
          {
            title: "require",
            required: ["mode"],
            properties: {
              mode: {
                type: "string",
                const: "require",
                order: 0,
              },
            },
            description:
              "Always require encryption. If the source database server does not support encryption, connection will fail.",
            additionalProperties: true,
          },
          {
            title: "verify-ca",
            required: ["mode", "ca_certificate"],
            properties: {
              mode: {
                type: "string",
                const: "verify-ca",
                order: 0,
              },
              client_key: {
                type: "string",
                order: 3,
                title: "Client Key",
                multiline: true,
                description: "Client key",
                airbyte_secret: true,
              },
              ca_certificate: {
                type: "string",
                order: 1,
                title: "CA certificate",
                multiline: true,
                description: "CA certificate",
                airbyte_secret: true,
              },
              client_certificate: {
                type: "string",
                order: 2,
                title: "Client Certificate",
                multiline: true,
                description: "Client certificate",
                airbyte_secret: true,
              },
              client_key_password: {
                type: "string",
                order: 4,
                title: "Client key password",
                description:
                  "Password for keystorage. If you do not add it - the password will be generated automatically.",
                airbyte_secret: true,
              },
            },
            description:
              "Always require encryption and verifies that the source database server has a valid SSL certificate.",
            additionalProperties: true,
          },
          {
            title: "verify-full",
            required: ["mode", "ca_certificate"],
            properties: {
              mode: {
                type: "string",
                const: "verify-full",
                order: 0,
              },
              client_key: {
                type: "string",
                order: 3,
                title: "Client Key",
                multiline: true,
                description: "Client key",
                airbyte_secret: true,
              },
              ca_certificate: {
                type: "string",
                order: 1,
                title: "CA Certificate",
                multiline: true,
                description: "CA certificate",
                airbyte_secret: true,
              },
              client_certificate: {
                type: "string",
                order: 2,
                title: "Client Certificate",
                multiline: true,
                description: "Client certificate",
                airbyte_secret: true,
              },
              client_key_password: {
                type: "string",
                order: 4,
                title: "Client key password",
                description:
                  "Password for keystorage. If you do not add it - the password will be generated automatically.",
                airbyte_secret: true,
              },
            },
            description:
              "This is the most secure mode. Always require encryption and verifies the identity of the source database server.",
            additionalProperties: true,
          },
        ],
        order: 7,
        title: "SSL Modes",
        description:
          'SSL connection modes. \n  Read more <a href="https://jdbc.postgresql.org/documentation/head/ssl-client.html"> in the docs</a>.',
      },
      username: {
        type: "string",
        order: 4,
        title: "Username",
        description: "Username to access the database.",
      },
      tunnel_method: {
        type: "object",
        oneOf: [
          {
            title: "No Tunnel",
            required: ["tunnel_method"],
            properties: {
              tunnel_method: {
                type: "string",
                const: "NO_TUNNEL",
                order: 0,
                description: "No ssh tunnel needed to connect to database",
              },
            },
          },
          {
            title: "SSH Key Authentication",
            required: ["tunnel_method", "tunnel_host", "tunnel_port", "tunnel_user", "ssh_key"],
            properties: {
              ssh_key: {
                type: "string",
                order: 4,
                title: "SSH Private Key",
                multiline: true,
                description:
                  "OS-level user account ssh key credentials in RSA PEM format ( created with ssh-keygen -t rsa -m PEM -f myuser_rsa )",
                airbyte_secret: true,
              },
              tunnel_host: {
                type: "string",
                order: 1,
                title: "SSH Tunnel Jump Server Host",
                description: "Hostname of the jump server host that allows inbound ssh tunnel.",
              },
              tunnel_port: {
                type: "integer",
                order: 2,
                title: "SSH Connection Port",
                default: 22,
                maximum: 65536,
                minimum: 0,
                examples: ["22"],
                description: "Port on the proxy/jump server that accepts inbound ssh connections.",
              },
              tunnel_user: {
                type: "string",
                order: 3,
                title: "SSH Login Username",
                description: "OS-level username for logging into the jump server host.",
              },
              tunnel_method: {
                type: "string",
                const: "SSH_KEY_AUTH",
                order: 0,
                description: "Connect through a jump server tunnel host using username and ssh key",
              },
            },
          },
          {
            title: "Password Authentication",
            required: ["tunnel_method", "tunnel_host", "tunnel_port", "tunnel_user", "tunnel_user_password"],
            properties: {
              tunnel_host: {
                type: "string",
                order: 1,
                title: "SSH Tunnel Jump Server Host",
                description: "Hostname of the jump server host that allows inbound ssh tunnel.",
              },
              tunnel_port: {
                type: "integer",
                order: 2,
                title: "SSH Connection Port",
                default: 22,
                maximum: 65536,
                minimum: 0,
                examples: ["22"],
                description: "Port on the proxy/jump server that accepts inbound ssh connections.",
              },
              tunnel_user: {
                type: "string",
                order: 3,
                title: "SSH Login Username",
                description: "OS-level username for logging into the jump server host",
              },
              tunnel_method: {
                type: "string",
                const: "SSH_PASSWORD_AUTH",
                order: 0,
                description: "Connect through a jump server tunnel host using username and password authentication",
              },
              tunnel_user_password: {
                type: "string",
                order: 4,
                title: "Password",
                description: "OS-level password for logging into the jump server host",
                airbyte_secret: true,
              },
            },
          },
        ],
        title: "SSH Tunnel Method",
        description:
          "Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use.",
      },
      jdbc_url_params: {
        type: "string",
        order: 6,
        title: "JDBC URL Parameters (Advanced)",
        description:
          "Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (Eg. key1=value1&key2=value2&key3=value3). For more information read about <a href=\"https://jdbc.postgresql.org/documentation/head/connect.html\">JDBC URL parameters</a>.",
      },
      replication_method: {
        type: "object",
        oneOf: [
          {
            title: "Standard",
            required: ["method"],
            properties: {
              method: {
                type: "string",
                const: "Standard",
                order: 0,
              },
            },
            description:
              "Standard replication requires no setup on the DB side but will not be able to represent deletions incrementally.",
          },
          {
            title: "Logical Replication (CDC)",
            required: ["method", "replication_slot", "publication"],
            properties: {
              method: {
                type: "string",
                const: "CDC",
                order: 1,
              },
              plugin: {
                enum: ["pgoutput", "wal2json"],
                type: "string",
                order: 2,
                title: "Plugin",
                default: "pgoutput",
                description:
                  'A logical decoding plugin installed on the PostgreSQL server. The `pgoutput` plugin is used by default. If the replication table contains a lot of big jsonb values it is recommended to use `wal2json` plugin. Read more about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-2-select-a-replication-plugin">selecting replication plugins</a>.',
              },
              publication: {
                type: "string",
                order: 4,
                title: "Publication",
                description:
                  'A Postgres publication used for consuming changes. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-4-create-publications-and-replication-identities-for-tables">publications and replication identities</a>.',
              },
              replication_slot: {
                type: "string",
                order: 3,
                title: "Replication Slot",
                description:
                  'A plugin logical replication slot. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-3-create-replication-slot">replication slots</a>.',
              },
              lsn_commit_behaviour: {
                enum: ["While reading Data", "After loading Data in the destination"],
                type: "string",
                order: 6,
                title: "LSN commit behaviour",
                default: "After loading Data in the destination",
                description:
                  "Determines when Airbtye should flush the LSN of processed WAL logs in the source database. `After loading Data in the destination` is default. If `While reading Data` is selected, in case of a downstream failure (while loading data into the destination), next sync would result in a full sync.",
              },
              initial_waiting_seconds: {
                max: 1200,
                min: 120,
                type: "integer",
                order: 5,
                title: "Initial Waiting Time in Seconds (Advanced)",
                default: 300,
                description:
                  'The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-5-optional-set-up-initial-waiting-time">initial waiting time</a>.',
              },
            },
            description:
              'Logical replication uses the Postgres write-ahead log (WAL) to detect inserts, updates, and deletes. This needs to be configured on the source database itself. Only available on Postgres 10 and above. Read the <a href="https://docs.airbyte.com/integrations/sources/postgres">docs</a>.',
            additionalProperties: true,
          },
        ],
        order: 8,
        title: "Replication Method",
        description: "Replication method for extracting data from the database.",
      },
    },
  },
  jobInfo: {
    id: "1df56aba-ecee-4e65-b035-bfc1bc34cb2e",
    configType: "get_spec",
    configId: "Optional.empty",
    createdAt: 1674834137604,
    endedAt: 1674834137604,
    succeeded: true,
    connectorConfigurationUpdated: false,
    logs: {
      logLines: [],
    },
  },
};
