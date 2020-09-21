import React, { useMemo } from "react";
import { Formik, Form } from "formik";
import styled from "styled-components";

import { IDataItem } from "../DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";
import EditControls from "./components/EditControls";
import ConstructValidationSchema from "./components/ConstructValidationSchema";
import { specification } from "../../core/resources/SourceSpecification";

type formInitialValues = {
  [key: string]: any;
} & {
  name: string;
  serviceType: string;
  frequency?: string;
};

type IProps = {
  dropDownData: Array<IDataItem>;
  onDropDownSelect?: (id: string) => void;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    frequency?: string;
    connectionConfiguration: any;
  }) => void;
  formType: "source" | "destination" | "connection";
  formValues?: formInitialValues;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  specifications?: specification;
  documentation?: string;
};

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const ServiceForm: React.FC<IProps> = ({
  onSubmit,
  formType,
  dropDownData,
  formValues,
  onDropDownSelect,
  hasSuccess,
  successMessage,
  errorMessage,
  specifications,
  documentation
}) => {
  const properties = Object.keys(specifications?.properties || {});

  const validationSchema = useMemo(
    () => ConstructValidationSchema(specifications, properties),
    [specifications, properties]
  );
  const additionalFields = properties
    ? Object.fromEntries([
        ...properties.map(item => {
          const condition = specifications?.properties[item];
          const value = formValues
            ? formValues[item]
            : condition.type === "boolean"
            ? false
            : "";
          return [item, value];
        })
      ])
    : null;

  const isEditMode = !!formValues;
  return (
    <Formik
      initialValues={{
        name: formValues?.name || "",
        serviceType: formValues?.serviceType || "",
        frequency: formValues?.frequency || "",
        ...additionalFields
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={validationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit({
          name: values.name,
          serviceType: values.serviceType,
          frequency: values.frequency,
          connectionConfiguration: Object.fromEntries([
            ...properties.map(item => [
              item,
              values[item] || additionalFields[item]
            ])
          ])
        });
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, values, resetForm }) => (
        <FormContainer>
          <FormContent
            dropDownData={dropDownData}
            formType={formType}
            setFieldValue={setFieldValue}
            values={values}
            isEditMode={isEditMode}
            onDropDownSelect={onDropDownSelect}
            specifications={specifications}
            properties={properties}
            documentation={documentation}
          />

          {isEditMode ? (
            <EditControls
              isSubmitting={isSubmitting}
              isValid={isValid}
              dirty={dirty}
              resetForm={resetForm}
              successMessage={successMessage}
            />
          ) : (
            <BottomBlock
              isSubmitting={isSubmitting}
              isValid={isValid}
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
