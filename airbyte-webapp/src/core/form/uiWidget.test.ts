import { jsonSchemaToUiWidget } from "core/jsonSchema/schemaToUiWidget";

import { FormBlock } from "./types";
import { buildPathInitialState } from "./uiWidget";

const formItems: FormBlock[] = [
  {
    _type: "formGroup",
    fieldKey: "key",
    path: "key",
    isRequired: true,
    jsonSchema: {
      type: "object",
      required: ["start_date", "credentials"],
      properties: {
        start_date: { type: "string" },
        credentials: {
          type: "object",
          oneOf: [
            {
              title: "api key",
              required: ["api_key"],
              properties: { api_key: { type: "string" } },
            },
            {
              title: "oauth",
              required: ["redirect_uri"],
              properties: {
                redirect_uri: {
                  type: "string",
                  examples: ["https://api.hubspot.com/"],
                },
              },
            },
          ],
        },
      },
    },
    properties: [
      {
        _type: "formItem",
        fieldKey: "start_date",
        path: "key.start_date",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formCondition",
        fieldKey: "credentials",
        path: "key.credentials",
        isRequired: true,
        conditions: {
          "api key": {
            title: "api key",
            _type: "formGroup",
            fieldKey: "credentials",
            path: "key.credentials",
            isRequired: false,
            jsonSchema: {
              title: "api key",
              required: ["api_key"],
              properties: { api_key: { type: "string" } },
            },
            properties: [
              {
                _type: "formItem",
                fieldKey: "api_key",
                path: "key.credentials.api_key",
                isRequired: true,
                type: "string",
              },
            ],
          },
          oauth: {
            title: "oauth",
            _type: "formGroup",
            fieldKey: "credentials",
            path: "key.credentials",
            isRequired: false,
            jsonSchema: {
              title: "oauth",
              required: ["redirect_uri"],
              properties: {
                redirect_uri: {
                  type: "string",
                  examples: ["https://api.hubspot.com/"],
                },
              },
            },
            properties: [
              {
                _type: "formItem",
                examples: ["https://api.hubspot.com/"],
                fieldKey: "redirect_uri",
                path: "key.credentials.redirect_uri",
                isRequired: true,
                type: "string",
              },
            ],
          },
        },
      },
    ],
  },
];

it("should select first key by default", () => {
  const uiWidgetState = buildPathInitialState(formItems, {});
  expect(uiWidgetState).toEqual({
    "key.credentials": {
      selectedItem: "api key",
    },
    "key.credentials.api_key": {},
    "key.start_date": {},
  });
});

it("should select key selected in default values", () => {
  const uiWidgetState = buildPathInitialState(
    formItems,
    {
      key: {
        credentials: {
          redirect_uri: "value",
        },
      },
    },
    {}
  );
  expect(uiWidgetState).toEqual({
    "key.credentials": {
      selectedItem: "oauth",
    },
    "key.credentials.redirect_uri": {},
    "key.start_date": {},
  });
});

it("should select correct key for enum", () => {
  const fields = jsonSchemaToUiWidget(
    JSON.parse(
      `{"type":"object","title":"File Source Spec","$schema":"http://json-schema.org/draft-07/schema#","required":["dataset_name","format","url","provider"],"properties":{"url":{"type":"string","description":"URL path to access the file to be replicated"},"format":{"enum":["csv","json","html","excel","feather","parquet","orc","pickle"],"type":"string","default":"csv","description":"File Format of the file to be replicated (Warning: some format may be experimental, please refer to docs)."},"provider":{"type":"object","oneOf":[{"title":"HTTPS: Public Web","required":["storage"],"properties":{"storage":{"enum":["HTTPS"],"type":"string","default":"HTTPS"}}},{"title":"GCS: Google Cloud Storage","required":["storage","reader_impl"],"properties":{"storage":{"enum":["GCS"],"type":"string","default":"GCS"},"reader_impl":{"enum":["smart_open","gcsfs"],"type":"string","default":"gcsfs","description":"This connector provides multiple methods to retrieve data from GCS using either smart-open python libraries or GCSFS"},"service_account_json":{"type":"string","description":"In order to access private Buckets stored on Google Cloud, this connector would need a service account json credentials with the proper permissions as described <a href=\\"https://cloud.google.com/iam/docs/service-accounts\\" target=\\"_blank\\">here</a>. Please generate the credentials.json file and copy/paste its content to this field (expecting JSON formats). If accessing publicly available data, this field is not necessary."}}},{"title":"S3: Amazon Web Services","required":["storage","reader_impl"],"properties":{"storage":{"enum":["S3"],"type":"string","default":"S3"},"reader_impl":{"enum":["smart_open","s3fs"],"type":"string","default":"s3fs","description":"This connector provides multiple methods to retrieve data from AWS S3 using either smart-open python libraries or S3FS"},"aws_access_key_id":{"type":"string","description":"In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary."},"aws_secret_access_key":{"type":"string","description":"In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary.","airbyte_secret":true}}},{"title":"SSH: Secure Shell","required":["storage","user","host"],"properties":{"host":{"type":"string"},"user":{"type":"string"},"storage":{"enum":["SSH"],"type":"string","default":"SSH"},"password":{"type":"string","airbyte_secret":true}}},{"title":"SFTP: Secure File Transfer Protocol","required":["storage","user","host"],"properties":{"host":{"type":"string"},"user":{"type":"string"},"storage":{"enum":["SFTP"],"type":"string","default":"SFTP"},"password":{"type":"string","airbyte_secret":true}}},{"title":"WebHDFS: HDFS REST API (Untested)","required":["storage","host","port"],"properties":{"host":{"type":"string"},"port":{"type":"number"},"storage":{"enum":["WebHDFS"],"type":"string","default":"WebHDFS","description":"WARNING: smart_open library provides the ability to stream files over this protocol but we haven't been able to test this as part of Airbyte yet, please use with caution. We would love to hear feedbacks from you if you are able or fail to use this!"}}},{"title":"Local Filesystem (limited)","required":["storage"],"properties":{"storage":{"enum":["local"],"type":"string","default":"local","description":"WARNING: Note that local storage URL available for read must start with the local mount \\"/local/\\" at the moment until we implement more advanced docker mounting options..."}}}],"default":"Public Web","description":"Storage Provider or Location of the file(s) to be replicated."},"dataset_name":{"type":"string","description":"Name of the final table where to replicate this file (should include only letters, numbers dash and underscores)"},"reader_options":{"type":"string","examples":["{}","{'sep': ' '}"],"description":"This should be a valid JSON string used by each reader/parser to provide additional options and tune its behavior"}},"additionalProperties":false}`
    ),
    "key"
  );

  const uiWidgetState = buildPathInitialState(
    [fields],
    {
      key: {
        provider: {
          storage: "GCS",
        },
      },
    },
    {}
  );
  expect(uiWidgetState).toEqual({
    "key.dataset_name": {},
    "key.format": {
      default: "csv",
    },
    "key.provider": {
      selectedItem: "GCS: Google Cloud Storage",
    },
    "key.provider.reader_impl": {
      default: "gcsfs",
    },
    "key.provider.service_account_json": {},
    "key.provider.storage": {
      const: "GCS",
      default: "GCS",
    },
    "key.reader_options": {},
    "key.url": {},
  });
});
