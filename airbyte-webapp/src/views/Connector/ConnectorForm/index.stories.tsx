import { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";

import { Card } from "components/ui/Card";

import { ConnectorDefinitionSpecification, ConnectorSpecification } from "core/domain/connector";
import { isSourceDefinitionSpecification } from "core/domain/connector/source";

import { ConnectorForm } from "./ConnectorForm";

const TempConnector = {
  name: "Service",
  documentationUrl: "",
  sourceDefinitionId: "serviceId",
  dockerRepository: "",
  dockerImageTag: "",
  latestDockerImageTag: "",
  icon: "",
};

export default {
  title: "Connector/ConnectorForm",
  component: ConnectorForm,
  parameters: {
    actions: { argTypesRegex: "^on.*" },
  },
  args: {
    formType: "source",
    formValues: {
      serviceType: TempConnector.sourceDefinitionId,
    },
    onSubmit: async (v) => console.log(v),
    availableServices: [TempConnector],
  },
} as ComponentMeta<typeof ConnectorForm>;

const Template: ComponentStory<typeof ConnectorForm> = (args: React.ComponentProps<typeof ConnectorForm>) => {
  const selectedSpecification = args.selectedConnectorDefinitionSpecification as ConnectorDefinitionSpecification;
  // Hack to allow devs to not specify sourceDefinitionId
  if (!ConnectorSpecification.id(selectedSpecification)) {
    if (isSourceDefinitionSpecification(selectedSpecification)) {
      selectedSpecification.sourceDefinitionId = TempConnector.sourceDefinitionId;
    }
  }

  if (args.selectedConnectorDefinitionSpecification?.documentationUrl) {
    args.selectedConnectorDefinitionSpecification.documentationUrl = "";
  }

  return (
    <Card title="Test">
      <ConnectorForm {...args} />
    </Card>
  );
};

export const Common = Template.bind({});
Common.args = {
  selectedConnectorDefinitionSpecification: {
    ...TempConnector,
    destinationDefinitionId: "some-id",
    jobInfo: {
      id: "some-id",
      createdAt: Date.now(),
      endedAt: Date.now() + 1,
      configType: "get_spec",
      succeeded: true,
    },
    connectionSpecification: JSON.parse(`{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "BigQuery Destination Spec",
    "type": "object",
    "required": ["project_id", "dataset_id"],
    "additionalProperties": true,
    "properties": {
      "big_query_client_buffer_size_mb": {
        "title": "Google BigQuery client chunk size",
        "description": "Google BigQuery client's chunk(buffer) size (MIN=1, MAX = 15) for each table. The default 15MiB value is used if not set explicitly. It's recommended to decrease value for big data sets migration for less HEAP memory consumption and avoiding crashes. For more details refer to https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html",
        "type": "integer",
        "minimum": 1,
        "maximum": 15,
        "default": 15,
        "examples": ["15"]
      },
      "project_id": {
        "type": "string",
        "description": "The GCP project ID for the project containing the target BigQuery dataset.",
        "title": "Project ID"
      },
      "dataset_id": {
        "type": "string",
        "description": "Default BigQuery Dataset ID tables are replicated to if the source does not specify a namespace.",
        "title": "Default Dataset ID"
      },
      "dataset_location": {
        "type": "string",
        "description": "The location of the dataset. Warning: Changes made after creation will not be applied.",
        "title": "Dataset Location",
        "default": "US",
        "enum": [
          "US",
          "EU",
          "asia-east1",
          "asia-east2",
          "asia-northeast1",
          "asia-northeast2",
          "asia-northeast3",
          "asia-south1",
          "asia-southeast1",
          "asia-southeast2",
          "australia-southeast1",
          "europe-central1",
          "europe-central2",
          "europe-north1",
          "europe-west1",
          "europe-west2",
          "europe-west3",
          "europe-west4",
          "europe-west5",
          "europe-west6",
          "northamerica-northeast1",
          "southamerica-east1",
          "us-central1",
          "us-east1",
          "us-east4",
          "us-west-1",
          "us-west-2",
          "us-west-3",
          "us-west-4"
        ]
      },
      "credentials_json": {
        "type": "string",
        "description": "The contents of the JSON service account key. Check out the <a href=\\"https://docs.airbyte.io/integrations/destinations/bigquery\\">docs</a> if you need help generating this key. Default credentials will be used if this field is left empty.",
        "title": "Credentials JSON",
        "airbyte_secret": true
      }
    }
  }`),
  },
};

export const Oneof = Template.bind({});
Oneof.args = {
  selectedConnectorDefinitionSpecification: {
    ...TempConnector,
    destinationDefinitionId: "some-other-id",
    jobInfo: {
      id: "some-id",
      createdAt: Date.now(),
      endedAt: Date.now() + 1,
      configType: "get_spec",
      succeeded: true,
    },
    connectionSpecification: JSON.parse(`{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MSSQL Source Spec",
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "ssl_method": {
        "title": "SSL Method",
        "type": "object",
        "description": "Encryption method to use when communicating with the database",
        "order": 6,
        "oneOf": [
          {
            "title": "Unencrypted",
            "additionalProperties": false,
            "description": "Data transfer will not be encrypted.",
            "required": ["ssl_method"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "unencrypted",
                "enum": ["unencrypted"],
                "default": "unencrypted"
              }
            }
          },
          {
            "title": "Encrypted (trust server certificate)",
            "additionalProperties": false,
            "description": "Use the cert provided by the server without verification.  (For testing purposes only!)",
            "required": ["ssl_method"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "encrypted_trust_server_certificate",
                "enum": ["encrypted_trust_server_certificate"],
                "default": "encrypted_trust_server_certificate"
              }
            }
          },
          {
            "title": "Encrypted (verify certificate)",
            "additionalProperties": false,
            "description": "Verify and use the cert provided by the server.",
            "required": ["ssl_method", "trustStoreName", "trustStorePassword"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "encrypted_verify_certificate",
                "enum": ["encrypted_verify_certificate"],
                "default": "encrypted_verify_certificate"
              },
              "hostNameInCertificate": {
                "title": "Host Name In Certificate",
                "type": "string",
                "description": "Specifies the host name of the server. The value of this property must match the subject property of the certificate.",
                "order": 7
              }
            }
          }
        ]
      }
    }
  }`),
  },
};
