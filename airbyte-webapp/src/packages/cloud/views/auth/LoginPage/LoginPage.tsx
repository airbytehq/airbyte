import React from "react";
import { Field, FieldProps, Formik } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { LabeledInput, Link, LoadingButton } from "components";
import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { FormTitle } from "../components/FormTitle";
import { FieldError } from "../../../lib/errors/FieldError";

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
});

const LoginPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { login } = useAuthService();

  return (
    <div>
      <FormTitle bold>Sign in to Airbyte</FormTitle>

      <Formik
        initialValues={{
          email: "",
          password: "",
        }}
        validationSchema={LoginPageValidationSchema}
        onSubmit={async (values, { setFieldError, setStatus }) =>
          login(values).catch((err) => {
            if (err instanceof FieldError) {
              setFieldError(err.field, err.message);
            } else {
              setStatus(err.message);
            }
          })
        }
        validateOnBlur
        validateOnChange={false}
      >
        {({ isSubmitting }) => (
          <Form>
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="form.yourEmail" />}
                    placeholder={formatMessage({
                      id: "form.email.placeholder",
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
                    label={"Password"}
                    placeholder={"Enter a strong password"}
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
            <BottomBlock>
              <>
                <Link to={"/reset-password"} $light>
                  Forgot your password
                </Link>
                <LoadingButton type="submit" isLoading={isSubmitting}>
                  Log In
                </LoadingButton>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default LoginPage;
