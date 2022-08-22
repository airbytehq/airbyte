import { Field, FieldProps, Formik } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";

import { useConfig } from "config";
import { useExperiment } from "hooks/services/Experiment";
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
}

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

export const Disclaimer: React.FC = () => {
  const config = useConfig();
  return (
    <div className={styles.disclaimer}>
      <FormattedMessage
        id="login.disclaimer"
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
    </div>
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

  const showName = !useExperiment("authPage.signup.hideName", false);
  const showCompanyName = !useExperiment("authPage.signup.hideCompanyName", false);

  const validationSchema = useMemo(() => {
    const shape = {
      email: yup.string().email("form.email.error").required("form.empty.error"),
      password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
      name: yup.string(),
      companyName: yup.string(),
    };
    if (showName) {
      shape.name = shape.name.required("form.empty.error");
    }
    if (showCompanyName) {
      shape.companyName = shape.companyName.required("form.empty.error");
    }
    return yup.object().shape(shape);
  }, [showName, showCompanyName]);

  return (
    <Formik<FormValues>
      initialValues={{
        name: "",
        companyName: "",
        email: "",
        password: "",
        news: true,
      }}
      validationSchema={validationSchema}
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
      {({ isValid, isSubmitting, status }) => (
        <Form>
          {(showName || showCompanyName) && (
            <RowFieldItem>
              {showName && <NameField />}
              {showCompanyName && <CompanyNameField />}
            </RowFieldItem>
          )}

          <FieldItem>
            <EmailField />
          </FieldItem>
          <FieldItem>
            <PasswordField />
          </FieldItem>
          <FieldItem>
            <NewsField />
          </FieldItem>
          <BottomBlock>
            <SignupButton isLoading={isSubmitting} disabled={!isValid} />
            {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
          </BottomBlock>
        </Form>
      )}
    </Formik>
  );
};
