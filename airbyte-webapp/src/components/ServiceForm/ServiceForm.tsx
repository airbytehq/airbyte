import React from "react";
import { Formik, Form } from "formik";
import styled from "styled-components";

import { IDataItem } from "../DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";
import EditControls from "./components/EditControls";
import { specification } from "../../core/resources/SourceSpecification";
import { useBuildForm, FormInitialValues } from "./useBuildForm";

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
  specifications?: specification;
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
  const properties = Object.keys(specifications?.properties || {});

  const serviceValues = {
    name: "",
    serviceType: "",
    ...formValues
  };

  const { formFields, initialValues, validationSchema } = useBuildForm(
    serviceValues,
    formType,
    specifications
  );

  return (
    <Formik
      initialValues={initialValues}
      validateOnBlur={true}
      validateOnChange={true}
      validateOnMount={true}
      validationSchema={() => validationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit(values);
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, values, resetForm }) => (
        <FormContainer>
          <FormContent
            allowChangeConnector={allowChangeConnector}
            dropDownData={dropDownData}
            formType={formType}
            formFields={formFields}
            setFieldValue={setFieldValue}
            values={values}
            isEditMode={isEditMode}
            onDropDownSelect={onDropDownSelect}
            specifications={specifications}
            properties={properties}
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
