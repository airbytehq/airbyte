import React, { useCallback, useMemo, useState } from "react";
import { Formik } from "formik";
import { JSONSchema7 } from "json-schema";

import {
  useBuildForm,
  useBuildUiWidgets,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";
import { ServiceFormValues } from "./types";
import { ServiceFormContextProvider } from "./serviceFormContext";
import { FormRoot } from "./FormRoot";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import { FormBaseItem } from "core/form/types";
import { ConnectorNameControl } from "./components/Controls/ConnectorNameControl";
import { ConnectorServiceTypeControl } from "./components/Controls/ConnectorServiceTypeControl";
import { isSourceDefinition } from "core/domain/connector/source";

type ServiceFormProps = {
  formType: "source" | "destination";
  availableServices: (SourceDefinition | DestinationDefinition)[];
  onSubmit: (values: ServiceFormValues) => void;
  onRetest?: (values: ServiceFormValues) => void;
  specifications?: JSONSchema7;
  documentationUrl?: string;
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  additionBottomControls?: React.ReactNode;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  onServiceSelect?: (id: string) => void;
};

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const [isOpenRequestModal, setIsOpenRequestModal] = useState(false);

  const {
    specifications,
    formType,
    formValues,
    onSubmit,
    isLoading,
    onRetest,
  } = props;
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
            documentationUrl={props.documentationUrl}
            onChangeServiceType={props.onServiceSelect}
            availableServices={props.availableServices}
            allowChangeConnector={props.allowChangeConnector}
            isEditMode={props.isEditMode}
            onOpenRequestConnectorModal={() => setIsOpenRequestModal(true)}
          />
        ),
      },
    }),
    [
      formType,
      setIsOpenRequestModal,
      props.allowChangeConnector,
      props.availableServices,
      props.documentationUrl,
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
                (s) =>
                  (isSourceDefinition(s)
                    ? s.sourceDefinitionId
                    : s.destinationDefinitionId) === values.serviceType
              )}
              formFields={formFields}
            />
            {isOpenRequestModal && (
              <RequestConnectorModal
                connectorType={formType}
                onClose={() => setIsOpenRequestModal(false)}
              />
            )}
          </ServiceFormContextProvider>
        )}
      </Formik>
    </>
  );
};

export default ServiceForm;
