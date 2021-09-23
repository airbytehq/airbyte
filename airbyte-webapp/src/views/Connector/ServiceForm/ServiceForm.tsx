import React, { useCallback, useMemo } from "react";
import { Formik } from "formik";
import { JSONSchema7 } from "json-schema";
import { useToggle } from "react-use";

import {
  useBuildForm,
  useBuildInitialSchema,
  useBuildUiWidgets,
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
  Connector,
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
    selectedConnector,
    onRetest,
  } = props;

  const specifications = useBuildInitialSchema(selectedConnector);

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        name: { type: "string" },
        serviceType: { type: "string" },
        ...Object.fromEntries(
          Object.entries({
            connectionConfiguration: isLoading
              ? null
              : {
                  type: "object",
                  properties: {
                    host: {
                      type: "string",
                      description: "Hostname of the database.",
                      title: "Host",
                    },
                    port: {
                      title: "Port",
                      type: "integer",
                      description: "Port of the database.",
                    },
                    password: {
                      title: "Password",
                      airbyte_secret: true,
                      type: "string",
                      description: "Password associated with the username.",
                    },
                    credentials: {
                      type: "object",
                      oneOf: [
                        {
                          title: "api key",
                          properties: {
                            api_key: {
                              type: "string",
                            },
                          },
                        },
                        {
                          title: "oauth",
                          properties: {
                            redirect_uri: {
                              type: "string",
                              examples: ["https://api.hubspot.com/"],
                            },
                          },
                        },
                      ],
                    },
                    message: {
                      type: "string",
                      multiline: true,
                      title: "Message",
                    },
                    priceList: {
                      type: "array",
                      items: {
                        type: "object",
                        properties: {
                          name: {
                            type: "string",
                            title: "Product name",
                          },
                          price: {
                            type: "integer",
                            title: "Price ($)",
                          },
                        },
                      },
                    },
                    emails: {
                      type: "array",
                      items: {
                        type: "string",
                      },
                    },
                    workTime: {
                      type: "array",
                      title: "Work time",
                      items: {
                        type: "string",
                        enum: ["day", "night"],
                      },
                    },
                  },
                },
          }).filter(([, v]) => !!v)
        ),
      },
      required: ["name", "serviceType"],
    }),
    [isLoading, specifications]
  );

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

  const { formFields, initialValues } = useBuildForm(jsonSchema, formValues);

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgets(
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
              selectedService={props.availableServices.find(
                (s) => Connector.id(s) === values.serviceType
              )}
              selectedConnector={props.selectedConnector}
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
