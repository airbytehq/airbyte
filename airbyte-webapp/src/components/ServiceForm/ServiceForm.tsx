import React, { useMemo } from "react";
import { Formik, Form } from "formik";
import styled from "styled-components";

import { IDataItem } from "../DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";
import EditControls from "./components/EditControls";
import ConstructValidationSchema from "./components/ConstructValidationSchema";
import {
  propertiesType,
  specification
} from "../../core/resources/SourceSpecification";

type formInitialValues = {
  [key: string]: any;
} & {
  name: string;
  serviceType: string;
  frequency?: string;
};

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
    connectionConfiguration: any;
  }) => void;
  formType: "source" | "destination" | "connection";
  formValues?: formInitialValues;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  specifications?: specification;
  documentationUrl?: string;
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
  documentationUrl,
  isLoading,
  allowChangeConnector,
  isEditMode
}) => {
  const properties = Object.keys(specifications?.properties || {});

  const validationSchema = useMemo(
    () => ConstructValidationSchema(specifications, properties),
    [specifications, properties]
  );
  const getFieldValue = (condition: propertiesType) => {
    if (condition.default) {
      return condition.default;
    }
    if (condition.type === "boolean") {
      return false;
    }

    return "";
  };
  const additionalFields = properties
    ? Object.fromEntries([
        ...properties.map(item => {
          const condition = specifications?.properties[item];
          const value = formValues?.[item] || getFieldValue(condition);
          return [item, value];
        })
      ])
    : null;

  return (
    <Formik
      initialValues={{
        name: "",
        serviceType: "",
        frequency: "",
        ...additionalFields,
        ...formValues
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validateOnMount={true}
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
            allowChangeConnector={allowChangeConnector}
            dropDownData={dropDownData}
            formType={formType}
            setFieldValue={setFieldValue}
            values={values}
            isEditMode={isEditMode}
            onDropDownSelect={onDropDownSelect}
            specifications={specifications}
            properties={properties}
            documentationUrl={documentationUrl}
            isLoadSchema={isLoading}
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
