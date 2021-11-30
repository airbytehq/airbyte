import React, { useCallback, useMemo } from "react";
import { Formik } from "formik";
import { JSONSchema7 } from "json-schema";
import { useToggle } from "react-use";

import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgetsContext,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";
import { ServiceFormValues } from "./types";
import { ServiceFormContextProvider } from "./serviceFormContext";
import { FormRoot } from "./FormRoot";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";
import { FormBaseItem } from "core/form/types";
import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorServiceTypeControl } from "./components/Controls/ConnectorServiceTypeControl";
import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
} from "core/domain/connector";

type ServiceFormProps = {
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  selectedConnector?: ConnectorDefinitionSpecification;
  onServiceSelect?: (id: string) => void;
  onSubmit: (values: ServiceFormValues) => void;
  onRetest?: (values: ServiceFormValues) => void;
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  additionBottomControls?: React.ReactNode;
  fetchingConnectorError?: Error;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
};

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const [isOpenRequestModal, toggleOpenRequestModal] = useToggle(false);
  const {
    formType,
    formValues,
    onSubmit,
    isLoading,
    // selectedConnector,
    onRetest,
  } = props;

  const selectedConnector: any = {
    documentationUrl: "https://docs.airbyte.io/integrations/sources/harvest",
    connectionSpecification: {
      $schema: "http://json-schema.org/draft-07/schema#",
      title: "Harvest Spec",
      type: "object",
      required: ["account_id", "replication_start_date"],
      additionalProperties: true,
      properties: {
        account_id: {
          title: "Account ID",
          description:
            "Harvest account ID. Required for all Harvest requests in pair with API Key",
          airbyte_secret: true,
          type: "string",
          order: 0,
        },
        replication_start_date: {
          title: "Replication Start Date",
          description:
            "UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
          pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
          examples: ["2017-01-25T00:00:00Z"],
          type: "string",
          order: 1,
        },
        credentials: {
          title: "Authentication mechanism",
          description: "Choose how to authenticate to Harvest",
          type: "object",
          order: 2,
          oneOf: [
            {
              type: "object",
              title: "Authenticate via Harvest (Oauth)",
              required: ["client_id", "client_secret", "refresh_token"],
              additionalProperties: false,
              properties: {
                auth_type: {
                  type: "string",
                  const: "Client",
                  enum: ["Client"],
                  default: "Client",
                  order: 0,
                },
                client_id: {
                  title: "Client ID",
                  type: "string",
                  description: "The Client ID of your application",
                },
                client_secret: {
                  title: "Client Secret",
                  type: "string",
                  description: "The client secret of your application",
                  airbyte_secret: true,
                },
                refresh_token: {
                  title: "Refresh Token",
                  type: "string",
                  description:
                    "A refresh token generated using the above client ID and secret",
                  airbyte_secret: true,
                },
              },
            },
            {
              type: "object",
              title: "Authenticate with Personal Access Token",
              required: ["api_token"],
              additionalProperties: false,
              properties: {
                auth_type: {
                  type: "string",
                  const: "Token",
                  enum: ["Token"],
                  default: "Token",
                  order: 0,
                },
                api_token: {
                  title: "Personal Access Token",
                  description:
                    'Log into Harvest and then create new <a href="https://id.getharvest.com/developers"> personal access token</a>.',
                  type: "string",
                  airbyte_secret: true,
                },
              },
            },
          ],
        },
      },
    },
    supportsIncremental: true,
    supported_destination_sync_modes: ["append"],
    // authSpecification: {
    //   auth_type: "oauth2.0",
    //   oauth2Specification: {
    //     rootObject: ["credentials", 0],
    //     oauthFlowInitParameters: [["client_id"], ["client_secret"]],
    //     oauthFlowOutputParameters: [["refresh_token"]],
    //   },
    // },
    advancedAuth: {
      auth_flow_type: "oauth2.0",
      predicate_key: ["credentials", "auth_type"],
      predicate_value: "Client",
      oauth_config_specification: {
        complete_oauth_output_specification: {
          type: "object",
          additionalProperties: false,
          properties: {
            refresh_token: {
              type: "string",
              path_in_connector_config: ["credentials", "refresh_token"],
            },
          },
        },
        complete_oauth_server_input_specification: {
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
        complete_oauth_server_output_specification: {
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
    },
  };

  const specifications = useBuildInitialSchema(selectedConnector);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        name: { type: "string" },
        serviceType: { type: "string" },
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading ? null : specifications,
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name", "serviceType"],
    }),
    [isLoading, specifications]
  );

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  const uiOverrides = useMemo(
    () => ({
      name: {
        component: (property: FormBaseItem) => (
          <ConnectorNameControl property={property} formType={formType} />
        ),
      },
      serviceType: {
        component: (property: FormBaseItem) => (
          <ConnectorServiceTypeControl
            property={property}
            formType={formType}
            documentationUrl={selectedConnector?.documentationUrl}
            onChangeServiceType={props.onServiceSelect}
            availableServices={props.availableServices}
            allowChangeConnector={props.allowChangeConnector}
            isEditMode={props.isEditMode}
            onOpenRequestConnectorModal={toggleOpenRequestModal}
          />
        ),
      },
    }),
    [
      formType,
      toggleOpenRequestModal,
      props.allowChangeConnector,
      props.availableServices,
      props.selectedConnector,
      props.isEditMode,
      props.onServiceSelect,
    ]
  );

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgetsContext(
    formFields,
    initialValues,
    uiOverrides
  );

  const validationSchema = useConstructValidationSchema(
    uiWidgetsInfo,
    jsonSchema
  );

  const onFormSubmit = useCallback(
    async (values) => {
      const valuesToSend = validationSchema.cast(values, {
        stripUnknown: true,
      });
      return onSubmit(valuesToSend);
    },
    [onSubmit, validationSchema]
  );

  const onRetestForm = useCallback(
    async (values) => {
      if (!onRetest) {
        return null;
      }
      const valuesToSend = validationSchema.cast(values, {
        stripUnknown: true,
      });
      return onRetest(valuesToSend);
    },
    [onRetest, validationSchema]
  );

  return (
    <>
      <Formik
        validateOnBlur={true}
        validateOnChange={true}
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={onFormSubmit}
      >
        {({ values, setSubmitting }) => (
          <ServiceFormContextProvider
            widgetsInfo={uiWidgetsInfo}
            setUiWidgetsInfo={setUiWidgetsInfo}
            formType={formType}
            availableServices={props.availableServices}
            selectedConnector={selectedConnector}
            isEditMode={props.isEditMode}
            isLoadingSchema={props.isLoading}
          >
            <FormikPatch />
            <FormRoot
              {...props}
              onRetest={async () => {
                setSubmitting(true);
                await onRetestForm(values);
                setSubmitting(false);
              }}
              formFields={formFields}
            />
            {isOpenRequestModal && (
              <RequestConnectorModal
                connectorType={formType}
                onClose={toggleOpenRequestModal}
              />
            )}
          </ServiceFormContextProvider>
        )}
      </Formik>
    </>
  );
};
export default ServiceForm;
