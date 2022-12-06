import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput } from "components";
import { Separator } from "components/Separator";

const paymentFormSchema = yup.object().shape({
  nameOnCard: yup.string().email("login.email.error").required("email.empty.error"),
  password: yup.string().required("password.empty.error"),
});

const FormContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-left: 80px;
`;

const PaymentForm: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <FormContainer>
      <Formik
        initialValues={{ nameOnCard: "", password: "" }}
        validationSchema={paymentFormSchema}
        onSubmit={(values) => console.log(values)}
        validateOnBlur
        validateOnChange
      >
        {({}) => (
          <>
            <Field name="nameOnCard">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label="Name on card"
                  type="text"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
            <Separator height="" />
            <Field name="password">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label="Card details"
                  type="text"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
          </>
        )}
      </Formik>
    </FormContainer>
  );
};

export default PaymentForm;
