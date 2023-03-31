import { Formik, Field, FieldProps } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput } from "components";

import { FieldItem } from "../../components/FormComponents";
import { FormContainer, SubmitButton, Title } from "./common";

interface ResetFormProps {
  onSubmit: () => void;
}

const ResetFormValidationSchema = yup.object().shape({
  password: yup.string().email("resetPassword.reset.form.password.error").required("password.empty.error"),
  confirmPassword: yup.string().required("password.empty.error"),
});

const ResetPasswordForm: React.FC<ResetFormProps> = ({ onSubmit }) => {
  const { formatMessage } = useIntl();

  return (
    <>
      <Title>
        <FormattedMessage id="resetPassword.reset.title" />
      </Title>
      <Formik
        initialValues={{ password: "", confirmPassword: "" }}
        onSubmit={onSubmit}
        validationSchema={ResetFormValidationSchema}
        validateOnBlur
        validateOnChange
      >
        {({ isValid, dirty, isSubmitting }) => (
          <FormContainer>
            <FieldItem bottom="30">
              <Field name="password">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="resetPassword.reset.form.password" />}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem bottom="30">
              <Field name="confirmPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="resetPassword.reset.form.confirmPassword" />}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <SubmitButton white disabled={!(isValid && dirty)} type="submit" isLoading={isSubmitting}>
              <FormattedMessage id="resetPassword.reset.button" />
            </SubmitButton>
          </FormContainer>
        )}
      </Formik>
    </>
  );
};

export default ResetPasswordForm;
