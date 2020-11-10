import React from "react";
import { Formik, Form } from "formik";
import styled from "styled-components";
import { JSONSchema7 } from "json-schema";

import { IDataItem } from "../DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";
import EditControls from "./components/EditControls";
import {
  useBuildForm,
  FormInitialValues,
  useBuildUiWidgets,
  useConstructValidationSchema
} from "./useBuildForm";

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

type IProps = {
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  dropDownData: Array<IDataItem>;
  onDropDownSelect?: (id: string) => void;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    frequency?: string;
    connectionConfiguration?: any;
  }) => void;
  formType: "source" | "destination" | "connection";
  formValues?: Partial<FormInitialValues>;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  specifications?: JSONSchema7;
  documentationUrl?: string;
};

const ServiceForm: React.FC<IProps> = ({
  formType,
  dropDownData,
  specifications,
  formValues,
  onSubmit,
  onDropDownSelect,
  successMessage,
  errorMessage,
  documentationUrl,
  allowChangeConnector,
  hasSuccess,

  isLoading,
  isEditMode
}) => {
  const { formFields, initialValues } = useBuildForm(
    formType,
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

  return (
    <Formik
      initialValues={initialValues}
      validateOnBlur={true}
      validateOnChange={true}
      validateOnMount={true}
      validationSchema={validationSchema}
      onSubmit={async values =>
        onSubmit(validationSchema.cast(values, { stripUnknown: true }))
      }
    >
      {({ isSubmitting, isValid, dirty, resetForm, ...formProps }) => (
        <FormContainer>
          <FormContent
            {...formProps}
            allowChangeConnector={allowChangeConnector}
            schema={validationSchema}
            dropDownData={dropDownData}
            formType={formType}
            formFields={formFields}
            widgetsInfo={uiWidgetsInfo}
            isEditMode={isEditMode}
            isLoadingSchema={isLoading}
            onChangeServiceType={onDropDownSelect}
            setUiWidgetsInfo={setUiWidgetsInfo}
            documentationUrl={documentationUrl}
          />

          {isEditMode ? (
            <EditControls
              isSubmitting={isSubmitting}
              isValid={isValid}
              dirty={dirty}
              resetForm={resetForm}
              successMessage={successMessage}
              errorMessage={errorMessage}
            />
          ) : (
            <BottomBlock
              isSubmitting={isSubmitting}
              isValid={isValid}
              isLoadSchema={isLoading}
              dirty={dirty}
              formType={formType}
              hasSuccess={hasSuccess}
              errorMessage={errorMessage}
            />
          )}
        </FormContainer>
      )}
    </Formik>
  );
};

export default ServiceForm;
