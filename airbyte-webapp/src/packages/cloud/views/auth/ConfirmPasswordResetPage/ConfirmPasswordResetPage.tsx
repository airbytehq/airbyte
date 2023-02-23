import { AuthErrorCodes } from "firebase/auth";
import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

import { LabeledInput, Link } from "components";
import { Button } from "components/ui/Button";
import { ToastType } from "components/ui/Toast";

import { useNotificationService } from "hooks/services/Notification/NotificationService";
import { useQuery } from "hooks/useQuery";
import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { BottomBlock, FieldItem, Form } from "../components/FormComponents";
import { FormTitle } from "../components/FormTitle";

const ResetPasswordPageValidationSchema = yup.object().shape({
  newPassword: yup.string().required("form.empty.error"),
});

const ResetPasswordConfirmPage: React.FC = () => {
  const { confirmPasswordReset } = useAuthService();
  const { registerNotification } = useNotificationService();
  const navigate = useNavigate();
  const query = useQuery<{ oobCode?: string }>();
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
            if (!query.oobCode) {
              return;
            }
            await confirmPasswordReset(query.oobCode, newPassword);
            registerNotification({
              id: "confirmResetPassword.success",
              text: formatMessage({ id: "confirmResetPassword.success" }),
              type: ToastType.SUCCESS,
            });
            navigate(CloudRoutes.Login);
          } catch (err) {
            // Error code reference:
            // https://firebase.google.com/docs/reference/js/v8/firebase.auth.Auth#confirmpasswordreset
            switch (err.code) {
              case AuthErrorCodes.EXPIRED_OOB_CODE:
                registerNotification({
                  id: "confirmResetPassword.error.expiredActionCode",
                  text: formatMessage({
                    id: "confirmResetPassword.error.expiredActionCode",
                  }),
                  type: ToastType.ERROR,
                });
                break;
              case AuthErrorCodes.INVALID_OOB_CODE:
                registerNotification({
                  id: "confirmResetPassword.error.invalidActionCode",
                  text: formatMessage({
                    id: "confirmResetPassword.error.invalidActionCode",
                  }),
                  type: ToastType.ERROR,
                });
                break;
              case AuthErrorCodes.WEAK_PASSWORD:
                registerNotification({
                  id: "confirmResetPassword.error.weakPassword",
                  text: formatMessage({
                    id: "confirmResetPassword.error.weakPassword",
                  }),
                  type: ToastType.WARNING,
                });
                break;
              default:
                registerNotification({
                  id: "confirmResetPassword.error.default",
                  text: formatMessage({
                    id: "confirmResetPassword.error.default",
                  }),
                  type: ToastType.ERROR,
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
              <Button type="submit" isLoading={isSubmitting} data-testid="login.resetPassword">
                <FormattedMessage id="login.resetPassword" />
              </Button>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export { ResetPasswordConfirmPage };
