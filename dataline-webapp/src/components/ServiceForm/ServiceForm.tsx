import React from "react";
import { Formik, Form } from "formik";
import * as yup from "yup";
import styled from "styled-components";

import { IDataItem } from "../DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";

type IProps = {
  dropDownData: Array<IDataItem>;
  onSubmit: () => void;
  formType: "source" | "destination";
};

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const onboardingValidationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
  serviceType: yup.string().required("form.empty.error")
});

const OnboardingForm: React.FC<IProps> = ({
  onSubmit,
  formType,
  dropDownData
}) => {
  return (
    <Formik
      initialValues={{
        name: "",
        serviceType: ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={onboardingValidationSchema}
      onSubmit={async (_, { setSubmitting }) => {
        setSubmitting(false);
        onSubmit();
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, values }) => (
        <FormContainer>
          <FormContent
            dropDownData={dropDownData}
            formType={formType}
            setFieldValue={setFieldValue}
            values={values}
          />

          <BottomBlock
            isSubmitting={isSubmitting}
            isValid={isValid}
            dirty={dirty}
            formType={formType}
          />
        </FormContainer>
      )}
    </Formik>
  );
};

export default OnboardingForm;
