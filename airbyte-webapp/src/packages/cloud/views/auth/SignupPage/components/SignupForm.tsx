import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";

import { useConfig } from "config";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CheckBoxControl from "../../components/CheckBoxControl";
import { BottomBlock, FieldItem, Form, RowFieldItem } from "../../components/FormComponents";
import styles from "./SignupForm.module.scss";

interface FormValues {
  name: string;
  companyName: string;
  email: string;
  password: string;
  news: boolean;
  security: boolean;
}

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  companyName: yup.string().required("form.empty.error"),
  security: yup.boolean().oneOf([true], "form.empty.error"),
});

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

export const NameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="name">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="login.fullName" />}
          placeholder={formatMessage({
            id: "login.fullName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const CompanyNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="companyName">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="login.companyName" />}
          placeholder={formatMessage({
            id: "login.companyName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const EmailField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="email">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="login.yourEmail" />}
          placeholder={formatMessage({
            id: "login.yourEmail.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const PasswordField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="password">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="login.password" />}
          placeholder={formatMessage({
            id: "login.password.placeholder",
          })}
          type="password"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const NewsField: React.FC = () => {
  const { formatMessage } = useIntl();
  return (
    <Field name="news">
      {({ field, meta }: FieldProps<string>) => (
        <MarginBlock>
          <CheckBoxControl
            {...field}
            checked={!!field.value}
            checkbox
            label={<FormattedMessage id="login.subscribe" />}
            message={meta.touched && meta.error && formatMessage({ id: meta.error })}
          />
        </MarginBlock>
      )}
    </Field>
  );
};

export const SecurityField: React.FC = () => {
  const { formatMessage } = useIntl();
  const config = useConfig();

  return (
    <Field name="security">
      {({ field, meta }: FieldProps<string>) => (
        <CheckBoxControl
          {...field}
          onChange={(e) => field.onChange(e)}
          checked={!!field.value}
          checkbox
          label={
            <FormattedMessage
              id="login.security"
              values={{
                terms: (terms: React.ReactNode) => (
                  <Link $clear target="_blank" href={config.links.termsLink} as="a">
                    {terms}
                  </Link>
                ),
                privacy: (privacy: React.ReactNode) => (
                  <Link $clear target="_blank" href={config.links.privacyLink} as="a">
                    {privacy}
                  </Link>
                ),
              }}
            />
          }
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

interface SignupButtonProps {
  isLoading: boolean;
  disabled: boolean;
  buttonMessageId?: string;
}

export const SignupButton: React.FC<SignupButtonProps> = ({
  isLoading,
  disabled,
  buttonMessageId = "login.signup.submitButton",
}) => (
  <LoadingButton className={styles.signUpButton} type="submit" isLoading={isLoading} disabled={disabled}>
    <FormattedMessage id={buttonMessageId} />
  </LoadingButton>
);

export const SignupFormStatusMessage: React.FC = ({ children }) => (
  <div className={styles.statusMessage}>{children}</div>
);

export const SignupForm: React.FC = () => {
  const { signUp } = useAuthService();

  return (
    <Formik<FormValues>
      initialValues={{
        name: "",
        companyName: "",
        email: "",
        password: "",
        news: true,
        security: false,
      }}
      validationSchema={SignupPageValidationSchema}
      onSubmit={async (values, { setFieldError, setStatus }) =>
        signUp(values).catch((err) => {
          if (err instanceof FieldError) {
            setFieldError(err.field, err.message);
          } else {
            setStatus(err.message);
          }
        })
      }
      validateOnBlur
      validateOnChange
    >
      {({ isValid, isSubmitting, values, status }) => (
        <Form>
          <RowFieldItem>
            <NameField />
            <CompanyNameField />
          </RowFieldItem>

          <FieldItem>
            <EmailField />
          </FieldItem>
          <FieldItem>
            <PasswordField />
          </FieldItem>
          <FieldItem>
            <NewsField />
            <SecurityField />
          </FieldItem>
          <BottomBlock>
            <SignupButton isLoading={isSubmitting} disabled={!isValid || !values.security} />
            {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
          </BottomBlock>
        </Form>
      )}
    </Formik>
  );
};
