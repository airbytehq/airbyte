import { AuthErrorCodes } from "firebase/auth";
import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";

import { useNotificationService } from "hooks/services/Notification/NotificationService";
import useRouterHook from "hooks/useRouter";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { FormTitle } from "../components/FormTitle";

const ResetPasswordPageValidationSchema = yup.object().shape({
  newPassword: yup.string().required("form.empty.error"),
});

const ResetPasswordConfirmPage: React.FC = () => {
  const { confirmPasswordReset } = useAuthService();
  const { registerNotification } = useNotificationService();
  const { push, query } = useRouterHook<{ oobCode: string }>();
  const { formatMessage } = useIntl();

  return (
    <div>
      <FormTitle>
        <FormattedMessage id="login.resetPassword" />
      </FormTitle>

      <Formik
        initialValues={{
          newPassword: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={async ({ newPassword }) => {
          try {
            await confirmPasswordReset(query.oobCode, newPassword);
            registerNotification({
              id: "confirmResetPassword.success",
              title: formatMessage({ id: "confirmResetPassword.success" }),
              isError: false,
            });
            push(CloudRoutes.Login);
          } catch (err) {
            // Error code reference:
            // https://firebase.google.com/docs/reference/js/v8/firebase.auth.Auth#confirmpasswordreset
            switch (err.code) {
              case AuthErrorCodes.EXPIRED_OOB_CODE:
                registerNotification({
                  id: "confirmResetPassword.error.expiredActionCode",
                  title: formatMessage({
                    id: "confirmResetPassword.error.expiredActionCode",
                  }),
                  isError: true,
                });
                break;
              case AuthErrorCodes.INVALID_OOB_CODE:
                registerNotification({
                  id: "confirmResetPassword.error.invalidActionCode",
                  title: formatMessage({
                    id: "confirmResetPassword.error.invalidActionCode",
                  }),
                  isError: true,
                });
                break;
              case AuthErrorCodes.WEAK_PASSWORD:
                registerNotification({
                  id: "confirmResetPassword.error.weakPassword",
                  title: formatMessage({
                    id: "confirmResetPassword.error.weakPassword",
                  }),
                  isError: true,
                });
                break;
              default:
                registerNotification({
                  id: "confirmResetPassword.error.default",
                  title: formatMessage({
                    id: "confirmResetPassword.error.default",
                  }),
                  isError: true,
                });
            }
          }
        }}
        validateOnBlur
        validateOnChange={false}
      >
        {({ isSubmitting }) => (
          <Form>
            <FieldItem>
              <Field name="newPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="confirmResetPassword.newPassword" />}
                    type="password"
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

export { ResetPasswordConfirmPage };
