import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import { AuthErrorCodes } from "firebase/auth";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";
import { LoadingButton } from "components";
import {
  useAuthService,
  useCurrentUser,
} from "packages/cloud/services/auth/AuthService";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";

export const PasswordSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { updatePassword } = useAuthService();
  const { email } = useCurrentUser();
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  return (
    <SettingsCard>
      <Content>
        <Formik
          initialValues={{
            currentPassword: "",
            newPassword: "",
            passwordConfirmation: "",
          }}
          onSubmit={(values, { setSubmitting, setFieldValue }) => {
            setSubmitting(true);

            setSuccessMessage("");
            setErrorMessage("");

            if (values.newPassword !== values.passwordConfirmation) {
              setErrorMessage(
                formatMessage({
                  id: "settings.accountSettings.error.newPasswordMismatch",
                })
              );
              setSubmitting(false);
              return;
            }

            if (values.currentPassword === values.newPassword) {
              setErrorMessage(
                formatMessage({
                  id: "settings.accountSettings.error.newPasswordSameAsCurrent",
                })
              );
              setSubmitting(false);
              return;
            }

            updatePassword(email, values.currentPassword, values.newPassword)
              .then(() => {
                setSuccessMessage(
                  formatMessage({
                    id: "settings.accountSettings.updatePasswordSuccess",
                  })
                );
                setFieldValue("currentPassword", "");
                setFieldValue("newPassword", "");
                setFieldValue("passwordConfirmation", "");
              })
              .catch((err) => {
                switch (err.code) {
                  case AuthErrorCodes.INVALID_PASSWORD:
                    setErrorMessage(
                      formatMessage({
                        id: "firebase.auth.error.invalidPassword",
                      })
                    );
                    break;
                  case AuthErrorCodes.NETWORK_REQUEST_FAILED:
                    setErrorMessage(
                      formatMessage({
                        id: "firebase.auth.error.networkRequestFailed",
                      })
                    );
                    break;
                  case AuthErrorCodes.TOO_MANY_ATTEMPTS_TRY_LATER:
                    setErrorMessage(
                      formatMessage({
                        id: "firebase.auth.error.tooManyRequests",
                      })
                    );
                    break;
                  default:
                    setErrorMessage(
                      formatMessage({
                        id: "settings.accountSettings.updatePasswordError",
                      }) + JSON.stringify(err)
                    );
                }
              })
              .finally(() => {
                setSubmitting(false);
              });
          }}
        >
          {({ isSubmitting }) => (
            <Form>
              <FieldItem>
                <Field name="currentPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.currentPassword" />
                      }
                      disabled={isSubmitting}
                      required={true}
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
                <Field name="newPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.newPassword" />
                      }
                      disabled={isSubmitting}
                      required={true}
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
                <Field name="passwordConfirmation">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.newPasswordConfirmation" />
                      }
                      disabled={isSubmitting}
                      required={true}
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
              <LoadingButton type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="settings.accountSettings.updatePassword" />
              </LoadingButton>
              <FeedbackBlock
                errorMessage={errorMessage}
                successMessage={successMessage}
                isLoading={isSubmitting}
              />
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};
