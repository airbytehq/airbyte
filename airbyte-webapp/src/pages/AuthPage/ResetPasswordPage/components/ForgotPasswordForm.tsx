import { Formik, Field, FieldProps } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput } from "components";
import { Separator } from "components/Separator";

import { RoutePaths } from "pages/routePaths";

import { FieldItem } from "../../components/FormComponents";
import { FormContainer, SubmitButton, Title, SubTitle, LinkContainer, Lnk } from "./common";

interface ForgotPasswordFormProps {
  onSubmit: () => void;
  isSuccessful?: boolean;
}

const ValidationSchema = yup.object().shape({
  email: yup.string().email("login.email.error").required("email.empty.error"),
});

const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({ onSubmit }) => {
  const { formatMessage } = useIntl();
  return (
    <>
      <Title>
        <FormattedMessage id="resetPassword.forgot.title" />
      </Title>
      <SubTitle>
        <FormattedMessage id="resetPassword.forgot.explain" />
      </SubTitle>
      <Formik
        initialValues={{ email: "" }}
        onSubmit={onSubmit}
        validationSchema={ValidationSchema}
        validateOnBlur
        validateOnChange
      >
        {({ isValid, dirty, isSubmitting }) => (
          <FormContainer>
            <FieldItem bottom="30">
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="login.yourEmail" />}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <SubmitButton white disabled={!(isValid && dirty)} type="submit" isLoading={isSubmitting}>
              <FormattedMessage id="resetPassword.forgot.button" />
            </SubmitButton>
            <Separator height="52px" />
            <LinkContainer>
              <Lnk to={`/${RoutePaths.Signin}`}>
                <FormattedMessage id="resetPassword.forgot.link" />
              </Lnk>
            </LinkContainer>
          </FormContainer>
        )}
      </Formik>
    </>
  );
};

export default ForgotPasswordForm;
