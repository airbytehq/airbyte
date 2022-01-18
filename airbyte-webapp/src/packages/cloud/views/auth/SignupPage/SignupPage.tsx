import React from "react";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Formik } from "formik";
import styled from "styled-components";

import { useConfig } from "config";

import {
  BottomBlock,
  FieldItem,
  Form,
  RowFieldItem,
} from "../components/FormComponents";
import { H1, LabeledInput, Link, LoadingButton } from "components";
import CheckBoxControl from "../components/CheckBoxControl";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import SpecialBlock from "./components/SpecialBlock";

type FormValues = {
  name: string;
  company: string;
  email: string;
  password: string;
  subscribe: boolean;
  security: boolean;
};

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup
    .string()
    .min(6, "signup.password.minLength")
    .required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  company: yup.string().required("form.empty.error"),
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
          company: "",
          email: "",
          password: "",
          subscribe: true,
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
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
              <Field name="company">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="login.companyName" />}
                    placeholder={formatMessage({
                      id: "login.companyName.placeholder",
                    })}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
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
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
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
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <FieldItem>
              <Field name="subscribe">
                {({ field, meta }: FieldProps<string>) => (
                  <MarginBlock>
                    <CheckBoxControl
                      {...field}
                      checked={!!field.value}
                      checkbox
                      label={<FormattedMessage id="login.subscribe" />}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
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
                          terms: (...terms: React.ReactNode[]) => (
                            <Link
                              $clear
                              target="_blank"
                              href={config.ui.termsLink}
                              as="a"
                            >
                              {terms}
                            </Link>
                          ),
                          privacy: (...privacy: React.ReactNode[]) => (
                            <Link
                              $clear
                              target="_blank"
                              href={config.ui.privacyLink}
                              as="a"
                            >
                              {privacy}
                            </Link>
                          ),
                        }}
                      />
                    }
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <BottomBlock>
              <>
                <div />
                <LoadingButton
                  type="submit"
                  isLoading={isSubmitting}
                  disabled={!isValid}
                >
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
