import React from "react";
import { Field, FieldProps, Formik } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { LabeledInput, Link, LoadingButton } from "components";
import {
  BottomBlock,
  FieldItem,
  Form,
} from "packages/cloud/views/auth/components/FormComponents";
import { FormTitle } from "packages/cloud/views/auth/components/FormTitle";
import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import useRouter from "hooks/useRouter";

const LoginPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().required("form.empty.error"),
});

const LoginPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { login } = useAuthService();
  const { location, replace } = useRouter();

  return (
    <div>
      <FormTitle bold>
        <FormattedMessage id="login.loginTitle" />
      </FormTitle>

      <Formik
        initialValues={{
          email: "",
          password: "",
        }}
        validationSchema={LoginPageValidationSchema}
        onSubmit={async (values, { setFieldError }) => {
          return login(values)
            .then((_) => replace(location.state?.from ?? "/"))
            .catch((err) => {
              if (err instanceof FieldError) {
                setFieldError(err.field, err.message);
              } else {
                setFieldError("password", err.message);
              }
            });
        }}
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
                    label={<FormattedMessage id="login.yourPassword" />}
                    placeholder={formatMessage({
                      id: "login.yourPassword.placeholder",
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
            <BottomBlock>
              <>
                <Link
                  to={CloudRoutes.ResetPassword}
                  $light
                  data-testid="reset-password-link"
                >
                  <FormattedMessage id="login.forgotPassword" />
                </Link>
                <LoadingButton type="submit" isLoading={isSubmitting}>
                  <FormattedMessage id="login.login" />
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
