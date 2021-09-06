import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";

export const PasswordSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  return (
    <SettingsCard>
      <Content>
        <Formik
          initialValues={{
            currentPassword: "********",
            repeatPassword: "",
            password: "",
          }}
          onSubmit={() => {
            throw new Error("Not implemented");
          }}
        >
          {() => (
            <Form>
              <FieldItem>
                <Field name="currentPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.currentPassword" />
                      }
                      disabled={true}
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
                <Field name="password">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.password" />
                      }
                      disabled={true}
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
                <Field name="repeatPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.repeatPassword" />
                      }
                      disabled={true}
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
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};
