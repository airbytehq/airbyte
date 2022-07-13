import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LoadingButton, LabeledInput, Link } from "components";
import HeadTitle from "components/HeadTitle";

import { useNotificationService } from "hooks/services/Notification/NotificationService";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { CloudRoutes } from "../../../cloudRoutes";
import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { FormTitle } from "../components/FormTitle";

const ResetPasswordPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const ResetPasswordPage: React.FC = () => {
  const { requirePasswordReset } = useAuthService();
  const { registerNotification } = useNotificationService();
  const { formatMessage } = useIntl();

  return (
    <div>
      <HeadTitle titles={[{ id: "login.resetPassword" }]} />
      <FormTitle>
        <FormattedMessage id="login.resetPassword" />
      </FormTitle>

      <Formik
        initialValues={{
          email: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={async ({ email }, FormikBag) => {
          try {
            await requirePasswordReset(email);
            registerNotification({
              id: "resetPassword.emailSent",
              title: formatMessage({ id: "login.resetPassword.emailSent" }),
              isError: false,
            });
          } catch (err) {
            err.message.includes("user-not-found")
              ? FormikBag.setFieldError("email", "login.yourEmail.notFound")
              : FormikBag.setFieldError("email", "login.unknownError");
          }
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
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>
            <BottomBlock>
              <Link to={CloudRoutes.Login} $light>
                <FormattedMessage id="login.backLogin" />
              </Link>
              <LoadingButton type="submit" isLoading={isSubmitting} data-testid="login.resetPassword">
                <FormattedMessage id="login.resetPassword" />
              </LoadingButton>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default ResetPasswordPage;
