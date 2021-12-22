import React from "react";
import { Field, FieldProps, Formik } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { LoadingButton, LabeledInput, Link } from "components";
import { FormTitle } from "../components/FormTitle";
import { CloudRoutes } from "../../../cloudRoutes";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useNotificationService } from "hooks/services/Notification/NotificationService";

const ResetPasswordPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const ResetPasswordPage: React.FC = () => {
  const { requirePasswordReset } = useAuthService();
  const { registerNotification } = useNotificationService();
  const formatMessage = useIntl().formatMessage;

  return (
    <div>
      <FormTitle bold>
        <FormattedMessage id="login.resetPassword" />
      </FormTitle>

      <Formik
        initialValues={{
          email: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={async ({ email }) => {
          await requirePasswordReset(email);
          registerNotification({
            id: "resetPassword.emailSent",
            title: formatMessage({ id: "login.resetPassword.emailSent" }),
            isError: false,
          });
        }}
        validateOnBlur={true}
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
            <BottomBlock>
              <Link to={CloudRoutes.Login} $light>
                <FormattedMessage id="login.backLogin" />
              </Link>
              <LoadingButton
                type="submit"
                isLoading={isSubmitting}
                data-testid="login.resetPassword"
              >
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
