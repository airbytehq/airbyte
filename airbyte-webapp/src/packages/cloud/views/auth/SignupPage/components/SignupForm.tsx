import { yupResolver } from "@hookform/resolvers/yup";
import { Field, FieldProps, Formik, Form } from "formik";
import React, { useMemo, useState } from "react";
import { Controller, FormProvider, useForm, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { useSearchParams } from "react-router-dom";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput, Link } from "components";
import { Button } from "components/ui/Button";

import { useExperiment } from "hooks/services/Experiment";
import { SignupSourceDropdown } from "packages/cloud/components/experiments/SignupSourceDropdown";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { isGdprCountry } from "utils/dataPrivacy";
import { links } from "utils/links";

import CheckBoxControl from "../../components/CheckBoxControl";
import { BottomBlock, FieldItem, RowFieldItem } from "../../components/FormComponents";
import styles from "./SignupForm.module.scss";

interface SingupFormValues {
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

export const RHFNameField: React.FC = () => {
  const { formatMessage } = useIntl();
  const { control } = useFormContext<SingupFormValues>();

  return (
    <Controller
      name="name"
      control={control}
      render={({ field, fieldState }) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="login.fullName" />}
          placeholder={formatMessage({
            id: "login.fullName.placeholder",
          })}
          type="text"
          error={!!fieldState.error && fieldState.isTouched}
          message={fieldState.isTouched && fieldState.error && formatMessage({ id: fieldState.error.message })}
        />
      )}
    />
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

export const RHFCompanyNameField: React.FC = () => {
  const { formatMessage } = useIntl();
  const { control } = useFormContext<SingupFormValues>();

  return (
    <Controller
      name="companyName"
      control={control}
      render={({ field, fieldState }) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="login.companyName" />}
          placeholder={formatMessage({
            id: "login.companyName.placeholder",
          })}
          type="text"
          error={!!fieldState.error && fieldState.isTouched}
          message={fieldState.isTouched && fieldState.error && formatMessage({ id: fieldState.error.message })}
        />
      )}
    />
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

export const RHFEmailField: React.FC<{ label?: React.ReactNode }> = () => {
  const { formatMessage } = useIntl();
  const { control } = useFormContext<SingupFormValues>();

  return (
    <Controller
      name="email"
      control={control}
      render={({ field, fieldState }) => {
        return (
          <LabeledInput
            {...field}
            label={<FormattedMessage id="login.yourEmail" />}
            placeholder={formatMessage({
              id: "login.yourEmail.placeholder",
            })}
            type="text"
            error={!!fieldState.error && fieldState.isTouched}
            message={fieldState.isTouched && fieldState.error && formatMessage({ id: fieldState.error.message })}
          />
        );
      }}
    />
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

export const RHFPasswordField: React.FC = () => {
  const { formatMessage } = useIntl();
  const { control } = useFormContext<SingupFormValues>();

  return (
    <Controller
      name="password"
      control={control}
      render={({ field, fieldState }) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="login.password" />}
          placeholder={formatMessage({
            id: "login.password.placeholder",
          })}
          type="password"
          error={!!fieldState.error && fieldState.isTouched}
          message={fieldState.isTouched && !!fieldState.error && formatMessage({ id: fieldState.error.message })}
        />
      )}
    />
  );
};

export const NewsField: React.FC = () => (
  <Field name="news">
    {({ field }: FieldProps<string>) => (
      <MarginBlock>
        <CheckBoxControl {...field} checked={!!field.value} label={<FormattedMessage id="login.subscribe" />} />
      </MarginBlock>
    )}
  </Field>
);

export const RHFNewsField: React.FC = () => {
  const { control } = useFormContext<SingupFormValues>();
  return (
    <Controller
      name="news"
      control={control}
      render={({ field }) => (
        <MarginBlock>
          <input type="checkbox" {...field} value="true" />
        </MarginBlock>
      )}
    />
  );
};

export const Disclaimer: React.FC = () => {
  return (
    <div className={styles.disclaimer}>
      <FormattedMessage
        id="login.disclaimer"
        values={{
          terms: (terms: React.ReactNode) => (
            <Link $clear target="_blank" href={links.termsLink} as="a">
              {terms}
            </Link>
          ),
          privacy: (privacy: React.ReactNode) => (
            <Link $clear target="_blank" href={links.privacyLink} as="a">
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
  <Button full size="lg" type="submit" isLoading={isLoading} disabled={disabled}>
    <FormattedMessage id={buttonMessageId} />
  </Button>
);

export const SignupFormStatusMessage: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <div className={styles.statusMessage}>{children}</div>
);

export const SignupForm: React.FC = () => {
  const { signUp } = useAuthService();
  const [status, setStatus] = useState(null);
  const showName = !useExperiment("authPage.signup.hideName", false);
  const showCompanyName = !useExperiment("authPage.signup.hideCompanyName", false);
  const showSourceSelector = useExperiment("authPage.signup.sourceSelector", false);

  const validationSchema = useMemo(() => {
    const shape = {
      email: yup.string().email("form.email.error").required("form.empty.error"),
      password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
      name: yup.string(),
      companyName: yup.string(),
      news: yup.boolean(),
    };
    if (showName) {
      shape.name = shape.name.required("form.empty.error");
    }
    if (showCompanyName) {
      shape.companyName = shape.companyName.required("form.empty.error");
    }
    return yup.object().shape(shape);
  }, [showName, showCompanyName]);

  const [params] = useSearchParams();
  const search = Object.fromEntries(params);

  const initialValues = {
    name: `${search.firstname ?? ""} ${search.lastname ?? ""}`.trim(),
    companyName: search.company ?? "",
    email: search.email ?? "",
    password: "",
    news: !isGdprCountry(),
  };
  const form = useForm<SingupFormValues>({
    resolver: yupResolver(validationSchema),
    reValidateMode: "onBlur",
    mode: "onChange",
    defaultValues: initialValues,
  });

  const onSubmit = form.handleSubmit(async (values) => {
    console.log(values);
    signUp(values).catch((err) => {
      if (err instanceof FieldError) {
        form.setError(err.field, { type: "string", message: err.message });
      } else {
        setStatus(err.message);
      }
    });
  });

  return (
    <FormProvider {...form}>
      <form onSubmit={onSubmit}>
        {(showName || showCompanyName) && (
          <RowFieldItem>
            {showName && <RHFNameField />}
            {showCompanyName && <RHFCompanyNameField />}
          </RowFieldItem>
        )}
        <FieldItem>
          <RHFEmailField />
        </FieldItem>
        <FieldItem>
          <RHFPasswordField />
        </FieldItem>
        <FieldItem>
          <RHFNewsField />
        </FieldItem>
        <BottomBlock>
          <SignupButton isLoading={form.formState.isSubmitting} disabled={!form.formState.isValid} />
          {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
        </BottomBlock>
        <h2>FormState</h2>
        <pre>{JSON.stringify(form.formState.errors, null, 2)}</pre>
        <button type="submit">Submit</button>
      </form>
    </FormProvider>
  );

  return (
    <Formik<SingupFormValues>
      initialValues={initialValues}
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
      {({ isValid, isSubmitting, status, values }) => (
        <Form>
          {(showName || showCompanyName) && (
            <RowFieldItem>
              {showName && <NameField />}
              {showCompanyName && <CompanyNameField />}
            </RowFieldItem>
          )}
          {/* exp-select-source-signup */}
          {showSourceSelector && (
            <FieldItem>
              <SignupSourceDropdown disabled={isSubmitting} email={values.email} />
            </FieldItem>
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
