import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";
import { LoadingButton } from "components";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";

import { usePassword } from "./hooks";
import { FormValues } from "./typings";

const PasswordSection: React.FC = () => {
  const { formatMessage } = useIntl();
  const { successMessage, errorMessage, changePassword } = usePassword();

  return (
    <SettingsCard>
      <Content>
        <Formik<FormValues>
          initialValues={{
            currentPassword: "",
            newPassword: "",
            passwordConfirmation: "",
          }}
          onSubmit={changePassword}
        >
          {({ isSubmitting, values }) => (
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
                      disabled={
                        isSubmitting || values.currentPassword.length === 0
                      }
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
                      disabled={
                        isSubmitting || values.currentPassword.length === 0
                      }
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

export default PasswordSection;
