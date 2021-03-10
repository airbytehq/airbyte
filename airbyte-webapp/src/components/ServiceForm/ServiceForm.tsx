import React, { useCallback } from "react";
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
  dropDownData: Array<DropDownRow.IDataItem>;
  onSubmit: (values: ServiceFormValues) => void;
  specifications?: JSONSchema7;
  isLoading?: boolean;
  isEditMode?: boolean;
  onDropDownSelect?: (id: string) => void;
  allowChangeConnector?: boolean;
  formValues?: Partial<ServiceFormValues>;
  hasSuccess?: boolean;
  additionBottomControls?: React.ReactNode;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  documentationUrl?: string;
};

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const ServiceForm: React.FC<ServiceFormProps> = (props) => {
  const { specifications, formValues, onSubmit, isLoading } = props;
  const { formFields, initialValues } = useBuildForm(
    isLoading,
    formValues,
    specifications
  );

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgets(
    formFields,
    initialValues
  );

  const validationSchema = useConstructValidationSchema(
    uiWidgetsInfo,
    specifications
  );

  const onFormSubmit = useCallback(
    async (values) => {
      return onSubmit(validationSchema.cast(values, { stripUnknown: true }));
    },
    [onSubmit, validationSchema]
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
        {({ values }) => (
          <>
            <FormikPatch />
            <FormRoot
              {...props}
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
