import React, { useCallback, useMemo } from "react";
import { Formik } from "formik";
import { JSONSchema7 } from "json-schema";

import { DropDownRow } from "components";

import {
  useBuildForm,
  useBuildUiWidgets,
  useConstructValidationSchema,
  usePatchFormik,
} from "./useBuildForm";
import { ServiceFormValues } from "./types";
import { ServiceFormContextProvider } from "./serviceFormContext";
import { FormRoot } from "./FormRoot";

type ServiceFormProps = {
  formType: "source" | "destination";
  onSubmit: (values: ServiceFormValues) => void;
  onRetest?: (values: ServiceFormValues) => void;
  specifications?: JSONSchema7;
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  additionBottomControls?: React.ReactNode;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  dropDownData: Array<DropDownRow.IDataItem>;
  onDropDownSelect?: (id: string) => void;
  documentationUrl?: string;
};

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const { specifications, formValues, onSubmit, isLoading, onRetest } = props;
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

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgets(
    formFields,
    initialValues
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
    [validationSchema, onRetest]
  );

  //  TODO: dropdownData should be map of entities instead of UI representation
  return (
    <ServiceFormContextProvider
      widgetsInfo={uiWidgetsInfo}
      setUiWidgetsInfo={setUiWidgetsInfo}
      formType={props.formType}
      isEditMode={props.isEditMode}
      allowChangeConnector={props.allowChangeConnector}
      isLoadingSchema={props.isLoading}
      onChangeServiceType={props.onDropDownSelect}
      dropDownData={props.dropDownData}
      documentationUrl={props.documentationUrl}
    >
      <Formik
        validateOnBlur={true}
        validateOnChange={true}
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={onFormSubmit}
      >
        {({ values, setSubmitting }) => (
          <>
            <FormikPatch />
            <FormRoot
              {...props}
              onRetest={async () => {
                setSubmitting(true);
                await onRetestForm(values);
                setSubmitting(false);
              }}
              formFields={formFields}
              connector={
                props.dropDownData?.find(
                  (item) => item.value === values.serviceType
                )?.text
              }
            />
          </>
        )}
      </Formik>
    </ServiceFormContextProvider>
  );
};

export default ServiceForm;
