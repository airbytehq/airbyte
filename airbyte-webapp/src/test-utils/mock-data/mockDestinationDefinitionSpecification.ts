import { DestinationDefinitionSpecificationRead } from "core/request/AirbyteClient";
import { ConnectorIds } from "utils/connectors";

export const mockDestinationDefinitionSpecification: DestinationDefinitionSpecificationRead = {
  destinationDefinitionId: ConnectorIds.Destinations.Postgres,
  documentationUrl: "https://docs.airbyte.io/integrations/destinations/postgres",
  connectionSpecification: {
    type: "object",
    title: "Postgres Destination Spec",
    $schema: "http://json-schema.org/draft-07/schema#",
    required: ["host", "port", "username", "database", "schema"],
    properties: {
      ssl: {
        type: "boolean",
        order: 6,
        title: "SSL Connection",
        default: false,
        description: "Encrypt data using SSL. When activating SSL, please select one of the connection modes.",
      },
      host: { type: "string", order: 0, title: "Host", description: "Hostname of the database." },
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
      schema: {
        type: "string",
        order: 3,
        title: "Default Schema",
        default: "public",
        examples: ["public"],
        description:
          'The default schema tables are written to if the source does not specify a namespace. The usual value for this field is "public".',
      },
      database: { type: "string", order: 2, title: "DB Name", description: "Name of the database." },
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
            properties: { mode: { enum: ["disable"], type: "string", const: "disable", order: 0, default: "disable" } },
            description: "Disable SSL.",
            additionalProperties: false,
          },
          {
            title: "allow",
            required: ["mode"],
            properties: { mode: { enum: ["allow"], type: "string", const: "allow", order: 0, default: "allow" } },
            description: "Allow SSL mode.",
            additionalProperties: false,
          },
          {
            title: "prefer",
            required: ["mode"],
            properties: { mode: { enum: ["prefer"], type: "string", const: "prefer", order: 0, default: "prefer" } },
            description: "Prefer SSL mode.",
            additionalProperties: false,
          },
          {
            title: "require",
            required: ["mode"],
            properties: { mode: { enum: ["require"], type: "string", const: "require", order: 0, default: "require" } },
            description: "Require SSL mode.",
            additionalProperties: false,
          },
          {
            title: "verify-ca",
            required: ["mode", "ca_certificate"],
            properties: {
              mode: { enum: ["verify-ca"], type: "string", const: "verify-ca", order: 0, default: "verify-ca" },
              ca_certificate: {
                type: "string",
                order: 1,
                title: "CA certificate",
                multiline: true,
                description: "CA certificate",
                airbyte_secret: true,
              },
              client_key_password: {
                type: "string",
                order: 4,
                title: "Client key password (Optional)",
                description:
                  "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
                airbyte_secret: true,
              },
            },
            description: "Verify-ca SSL mode.",
            additionalProperties: false,
          },
          {
            title: "verify-full",
            required: ["mode", "ca_certificate", "client_certificate", "client_key"],
            properties: {
              mode: { enum: ["verify-full"], type: "string", const: "verify-full", order: 0, default: "verify-full" },
              client_key: {
                type: "string",
                order: 3,
                title: "Client key",
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
                title: "Client certificate",
                multiline: true,
                description: "Client certificate",
                airbyte_secret: true,
              },
              client_key_password: {
                type: "string",
                order: 4,
                title: "Client key password (Optional)",
                description:
                  "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
                airbyte_secret: true,
              },
            },
            description: "Verify-full SSL mode.",
            additionalProperties: false,
          },
        ],
        order: 7,
        title: "SSL modes",
        description:
          'SSL connection modes. \n <b>disable</b> - Chose this mode to disable encryption of communication between Airbyte and destination database\n <b>allow</b> - Chose this mode to enable encryption only when required by the source database\n <b>prefer</b> - Chose this mode to allow unencrypted connection only if the source database does not support encryption\n <b>require</b> - Chose this mode to always require encryption. If the source database server does not support encryption, connection will fail\n  <b>verify-ca</b> - Chose this mode to always require encryption and to verify that the source database server has a valid SSL certificate\n  <b>verify-full</b> - This is the most secure mode. Chose this mode to always require encryption and to verify the identity of the source database server\n See more information - <a href="https://jdbc.postgresql.org/documentation/head/ssl-client.html"> in the docs</a>.',
      },
      username: { type: "string", order: 4, title: "User", description: "Username to use to access the database." },
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
        order: 8,
        title: "JDBC URL Params",
        description:
          "Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3).",
      },
    },
    additionalProperties: true,
  },
  jobInfo: {
    id: "0e3274aa-11da-4818-a750-4dc940cc7fdf",
    configType: "get_spec",
    configId: "Optional.empty",
    createdAt: 1669740943018,
    endedAt: 1669740943018,
    succeeded: true,
    logs: { logLines: [] },
  },
  supportedDestinationSyncModes: ["overwrite", "append", "append_dedup"],
};
