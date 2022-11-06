import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";

import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

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
                      label={<FormattedMessage id="settings.accountSettings.currentPassword" />}
                      disabled={isSubmitting}
                      required
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </FieldItem>
              <FieldItem>
                <Field name="newPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="settings.accountSettings.newPassword" />}
                      disabled={isSubmitting || values.currentPassword.length === 0}
                      required
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </FieldItem>
              <FieldItem>
                <Field name="passwordConfirmation">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="settings.accountSettings.newPasswordConfirmation" />}
                      disabled={isSubmitting || values.currentPassword.length === 0}
                      required
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </FieldItem>
              <Button type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="settings.accountSettings.updatePassword" />
              </Button>
              <FeedbackBlock errorMessage={errorMessage} successMessage={successMessage} isLoading={isSubmitting} />
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};

export default PasswordSection;
