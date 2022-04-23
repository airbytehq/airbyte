import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { H1, LabeledInput, Link, LoadingButton } from "components";

import { useConfig } from "config";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CheckBoxControl from "../components/CheckBoxControl";
import { BottomBlock, FieldItem, Form, RowFieldItem } from "../components/FormComponents";
import SpecialBlock from "./components/SpecialBlock";

type FormValues = {
  name: string;
  companyName: string;
  email: string;
  password: string;
  news: boolean;
  security: boolean;
};

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  companyName: yup.string().required("form.empty.error"),
  security: yup.boolean().oneOf([true], "form.empty.error"),
});

const SignupPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const config = useConfig();

  const { signUp } = useAuthService();

  return (
    <div>
      <H1 bold>
        <FormattedMessage id="login.activateAccess" />
      </H1>
      <SpecialBlock />

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
        validateOnBlur={true}
        validateOnChange={true}
      >
        {({ isValid, isSubmitting }) => (
          <Form>
            <RowFieldItem>
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
            </RowFieldItem>
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="login.yourEmail" />}
                    placeholder={formatMessage({
                      id: "login.yourEmail.placeholder",
                    })}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem>
              <Field name="password">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="login.password" />}
                    placeholder={formatMessage({
                      id: "login.password.placeholder",
                    })}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem>
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
                            <Link $clear target="_blank" href={config.ui.termsLink} as="a">
                              {terms}
                            </Link>
                          ),
                          privacy: (privacy: React.ReactNode) => (
                            <Link $clear target="_blank" href={config.ui.privacyLink} as="a">
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
            </FieldItem>
            <BottomBlock>
              <>
                <div />
                <LoadingButton type="submit" isLoading={isSubmitting} disabled={!isValid}>
                  <FormattedMessage id="login.signup" />
                </LoadingButton>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default SignupPage;
