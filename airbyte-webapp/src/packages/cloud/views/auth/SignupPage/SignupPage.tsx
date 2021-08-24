import React from "react";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Formik } from "formik";
import styled from "styled-components";

import {
  BottomBlock,
  FieldItem,
  Form,
  RowFieldItem,
} from "../components/FormComponents";
import { Button, H5, LabeledInput, Link } from "components";
import { FormTitle } from "../components/FormTitle";
import CheckBoxControl from "../components/CheckBoxControl";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import config from "config";

const MarginBlock = styled.div`
  margin-bottom: 15px;
`;

const SignupPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  company: yup.string().required("form.empty.error"),
  security: yup.boolean().required("form.empty.error"),
});

const SignupPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const { signUp } = useAuthService();

  return (
    <div>
      <FormTitle bold>
        <FormattedMessage id="login.activateAccess" />
      </FormTitle>
      <H5>
        <FormattedMessage id="login.activateAccess.subtitle" />
      </H5>

      <Formik
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
        validateOnChange={false}
      >
        {() => (
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
                <Button type="submit">
                  <FormattedMessage id="login.signup" />
                </Button>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default SignupPage;
