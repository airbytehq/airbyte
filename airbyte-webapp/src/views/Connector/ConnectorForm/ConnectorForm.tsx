import { Formik, getIn, setIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import React, { useCallback, useEffect, useMemo } from "react";
import { useDeepCompareEffect } from "react-use";

import { FormChangeTracker } from "components/common/FormChangeTracker";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBaseItem, FormComponentOverrideProps } from "core/form/types";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { isDefined } from "utils/common";

import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorFormContextProvider, useConnectorForm } from "./connectorFormContext";
import { FormRoot } from "./FormRoot";
import { ConnectorCardValues, ConnectorFormValues } from "./types";
import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

/**
 * This function sets all initial const values in the form to current values
 * @param schema
 * @param initialValues
 * @constructor
 */
const PatchInitialValuesWithWidgetConfig: React.FC<{
  schema: JSONSchema7;
  initialValues: ConnectorFormValues;
}> = ({ schema, initialValues }) => {
  const { widgetsInfo } = useConnectorForm();
  const { setFieldValue } = useFormikContext<ConnectorFormValues>();

  useDeepCompareEffect(() => {
    const widgetsInfoEntries = Object.entries(widgetsInfo);

    // set all const fields to form field values, so we could send form
    const patchedConstValues = widgetsInfoEntries
      .filter(([_, value]) => isDefined(value.const))
      .reduce((acc, [key, value]) => setIn(acc, key, value.const), initialValues);

    // set default fields as current values, so values could be populated correctly
    // fix for https://github.com/airbytehq/airbyte/issues/6791
    const patchedDefaultValues = widgetsInfoEntries
      .filter(([key, value]) => isDefined(value.default) && !isDefined(getIn(patchedConstValues, key)))
      .reduce((acc, [key, value]) => setIn(acc, key, value.default), patchedConstValues);

    if (patchedDefaultValues?.connectionConfiguration) {
      setTimeout(() => {
        // We need to push this out one execution slot, so the form isn't still in its
        // initialization status and won't react to this call but would just take the initialValues instead.
        setFieldValue("connectionConfiguration", patchedDefaultValues.connectionConfiguration);
      });
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [schema]);

  return null;
};

/**
 * Formik does not revalidate the form in case the validationSchema it's using changes.
 * This component just forces a revalidation of the form whenever the validation schema changes.
 */
const RevalidateOnValidationSchemaChange: React.FC<{ validationSchema: unknown }> = ({ validationSchema }) => {
  // The validationSchema is passed into this component instead of pulled from the FormikContext, since
  // due to https://github.com/jaredpalmer/formik/issues/2092 the validationSchema from the formik context will
  // always be undefined.
  const { validateForm } = useFormikContext();
  useEffect(() => {
    validateForm();
  }, [validateForm, validationSchema]);
  return null;
};

export interface ConnectorFormProps {
  formType: "source" | "destination";
  formId?: string;
  selectedConnectorDefinition?: ConnectorDefinition;
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  onSubmit: (values: ConnectorFormValues) => Promise<void> | void;
  isLoading?: boolean;
  isEditMode?: boolean;
  formValues?: Partial<ConnectorFormValues>;
  hasSuccess?: boolean;
  fetchingConnectorError?: Error | null;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  connectorId?: string;

  isTestConnectionInProgress?: boolean;
  onStopTesting?: () => void;
  testConnector?: (v?: ConnectorCardValues) => Promise<CheckConnectionRead>;
}

export const ConnectorForm: React.FC<ConnectorFormProps> = (props) => {
  const formId = useUniqueFormId(props.formId);
  const { clearFormChange } = useFormChangeTrackerService();

  const {
    formType,
    formValues,
    onSubmit,
    isLoading,
    isEditMode,
    isTestConnectionInProgress,
    onStopTesting,
    testConnector,
    selectedConnectorDefinition,
    selectedConnectorDefinitionSpecification,
    errorMessage,
    connectorId,
  } = props;

  if (selectedConnectorDefinitionSpecification) {
    selectedConnectorDefinitionSpecification.connectionSpecification = {
      type: "object",
      title: "Postgres Source Spec",
      $schema: "http://json-schema.org/draft-07/schema#",
      required: ["host", "port", "database", "username"],
      properties: {
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
          minItems: 2,
          required: true,
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
                  enum: ["disable"],
                  type: "string",
                  const: "disable",
                  order: 0,
                  default: "disable",
                },
              },
              description: "Disable SSL.",
              additionalProperties: false,
            },
            {
              title: "allow",
              required: ["mode"],
              properties: {
                mode: {
                  enum: ["allow"],
                  type: "string",
                  const: "allow",
                  order: 0,
                  default: "allow",
                },
              },
              description: "Allow SSL mode.",
              additionalProperties: false,
            },
            {
              title: "prefer",
              required: ["mode"],
              properties: {
                mode: {
                  enum: ["prefer"],
                  type: "string",
                  const: "prefer",
                  order: 0,
                  default: "prefer",
                },
              },
              description: "Prefer SSL mode.",
              additionalProperties: false,
            },
            {
              title: "require",
              required: ["mode"],
              properties: {
                mode: {
                  enum: ["require"],
                  type: "string",
                  const: "require",
                  order: 0,
                  default: "require",
                },
              },
              description: "Require SSL mode.",
              additionalProperties: false,
            },
            {
              title: "verify-ca",
              required: ["mode", "ca_certificate"],
              properties: {
                mode: {
                  enum: ["verify-ca"],
                  type: "string",
                  const: "verify-ca",
                  order: 0,
                  default: "verify-ca",
                },
                client_key: {
                  type: "string",
                  order: 3,
                  title: "Client Key (Optional)",
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
                  title: "Client Certificate (Optional)",
                  multiline: true,
                  description: "Client certificate",
                  airbyte_secret: true,
                },
                client_key_password: {
                  type: "string",
                  order: 4,
                  title: "Client key password (Optional)",
                  description:
                    "Password for keystorage. If you do not add it - the password will be generated automatically.",
                  airbyte_secret: true,
                },
              },
              description: "Verify-ca SSL mode.",
              additionalProperties: false,
            },
            {
              title: "verify-full",
              required: ["mode", "ca_certificate"],
              properties: {
                mode: {
                  enum: ["verify-full"],
                  type: "string",
                  const: "verify-full",
                  order: 0,
                  default: "verify-full",
                },
                client_key: {
                  type: "string",
                  order: 3,
                  title: "Client Key (Optional)",
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
                  title: "Client Certificate (Optional)",
                  multiline: true,
                  description: "Client certificate",
                  airbyte_secret: true,
                },
                client_key_password: {
                  type: "string",
                  order: 4,
                  title: "Client key password (Optional)",
                  description:
                    "Password for keystorage. If you do not add it - the password will be generated automatically.",
                  airbyte_secret: true,
                },
              },
              description: "Verify-full SSL mode.",
              additionalProperties: false,
            },
          ],
          order: 7,
          title: "SSL Modes",
          description:
            'SSL connection modes. \n <ul><li><b>disable</b> - Disables encryption of communication between Airbyte and source database</li>\n <li><b>allow</b> - Enables encryption only when required by the source database</li>\n <li><b>prefer</b> - allows unencrypted connection only if the source database does not support encryption</li>\n <li><b>require</b> - Always require encryption. If the source database server does not support encryption, connection will fail</li>\n  <li><b>verify-ca</b> - Always require encryption and verifies that the source database server has a valid SSL certificate</li>\n  <li><b>verify-full</b> - This is the most secure mode. Always require encryption and verifies the identity of the source database server</li></ul>\n Read more <a href="https://jdbc.postgresql.org/documentation/head/ssl-client.html"> in the docs</a>.',
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
                  enum: ["Standard"],
                  type: "string",
                  const: "Standard",
                  order: 0,
                  default: "Standard",
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
                  enum: ["CDC"],
                  type: "string",
                  const: "CDC",
                  order: 0,
                  default: "CDC",
                },
                plugin: {
                  enum: ["pgoutput", "wal2json"],
                  type: "string",
                  order: 1,
                  title: "Plugin",
                  default: "pgoutput",
                  description:
                    'A logical decoding plugin installed on the PostgreSQL server. The `pgoutput` plugin is used by default. If the replication table contains a lot of big jsonb values it is recommended to use `wal2json` plugin. Read more about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-2-select-a-replication-plugin">selecting replication plugins</a>.',
                },
                publication: {
                  type: "string",
                  order: 3,
                  title: "Publication",
                  description:
                    'A Postgres publication used for consuming changes. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-4-create-publications-and-replication-identities-for-tables">publications and replication identities</a>.',
                },
                replication_slot: {
                  type: "string",
                  order: 2,
                  title: "Replication Slot",
                  description:
                    'A plugin logical replication slot. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-3-create-replication-slot">replication slots</a>.',
                },
                initial_waiting_seconds: {
                  max: 1200,
                  min: 120,
                  type: "integer",
                  order: 4,
                  title: "Initial Waiting Time in Seconds (Advanced)",
                  default: 300,
                  description:
                    'The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds. Read about <a href="https://docs.airbyte.com/integrations/sources/postgres#step-5-optional-set-up-initial-waiting-time">initial waiting time</a>.',
                },
              },
              description:
                'Logical replication uses the Postgres write-ahead log (WAL) to detect inserts, updates, and deletes. This needs to be configured on the source database itself. Only available on Postgres 10 and above. Read the <a href="https://docs.airbyte.com/integrations/sources/postgres">docs</a>.',
            },
          ],
          order: 8,
          title: "Replication Method",
          description: "Replication method for extracting data from the database.",
        },
      },
    };
  }

  console.log(selectedConnectorDefinitionSpecification);

  const specifications = useBuildInitialSchema(selectedConnectorDefinitionSpecification);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        ...(selectedConnectorDefinitionSpecification ? { name: { type: "string" } } : {}),
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name"],
    }),
    [isLoading, selectedConnectorDefinitionSpecification, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  // Overrides default field label(i.e "Source name", "Destination name")
  const uiOverrides = useMemo(() => {
    return {
      name: {
        component: (property: FormBaseItem, componentProps: FormComponentOverrideProps) => (
          <ConnectorNameControl property={property} formType={formType} {...componentProps} />
        ),
      },
    };
  }, [formType]);

  const { uiWidgetsInfo, setUiWidgetsInfo, resetUiWidgetsInfo } = useBuildUiWidgetsContext(
    formFields,
    initialValues,
    uiOverrides
  );

  const validationSchema = useConstructValidationSchema(jsonSchema, uiWidgetsInfo);

  const getValues = useCallback(
    (values: ConnectorFormValues) =>
      validationSchema.cast(values, {
        stripUnknown: true,
      }),
    [validationSchema]
  );

  const onFormSubmit = useCallback(
    async (values: ConnectorFormValues) => {
      const valuesToSend = getValues(values);
      await onSubmit(valuesToSend);

      clearFormChange(formId);
    },
    [clearFormChange, formId, getValues, onSubmit]
  );

  return (
    <Formik
      validateOnBlur
      validateOnChange
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onFormSubmit}
      enableReinitialize
    >
      {({ dirty }) => (
        <ConnectorFormContextProvider
          formType={formType}
          widgetsInfo={uiWidgetsInfo}
          getValues={getValues}
          setUiWidgetsInfo={setUiWidgetsInfo}
          resetUiWidgetsInfo={resetUiWidgetsInfo}
          selectedConnectorDefinition={selectedConnectorDefinition}
          selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
          isEditMode={isEditMode}
          isLoadingSchema={isLoading}
          validationSchema={validationSchema}
          connectorId={connectorId}
        >
          <RevalidateOnValidationSchemaChange validationSchema={validationSchema} />
          <FormikPatch />
          <FormChangeTracker changed={dirty} formId={formId} />
          <PatchInitialValuesWithWidgetConfig schema={jsonSchema} initialValues={initialValues} />
          <FormRoot
            {...props}
            selectedConnector={selectedConnectorDefinitionSpecification}
            formFields={formFields}
            errorMessage={errorMessage}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTestingConnector={onStopTesting ? () => onStopTesting() : undefined}
            onRetest={testConnector ? async () => await testConnector() : undefined}
          />
        </ConnectorFormContextProvider>
      )}
    </Formik>
  );
};
