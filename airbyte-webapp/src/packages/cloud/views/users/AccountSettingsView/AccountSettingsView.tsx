import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Formik, Form, Field, FieldProps } from "formik";
import styled from "styled-components";

import { SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { LoadingButton, LabeledInput } from "components";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
`;

const AccountSettingsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { logout } = useAuthService();

  return (
    <>
      <SettingsCard title={<FormattedMessage id="settings.account" />}>
        <Formik
          initialValues={{
            firstName: "",
          }}
          onSubmit={() => {
            throw new Error("Not implemented");
          }}
        >
          {() =>
            (
              <Form>
                <Field name="firstName">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.form.firstName.label" />
                      }
                      placeholder={formatMessage({
                        id:
                          "settings.accountSettings.form.firstName.placeholder",
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
                <Field name="lastName">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.form.lastName.label" />
                      }
                      placeholder={formatMessage({
                        id:
                          "settings.accountSettings.form.lastName.placeholder",
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
                <Field name="email">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.form.email.label" />
                      }
                      placeholder={formatMessage({
                        id: "settings.accountSettings.form.email.placeholder",
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
              </Form>
            ) && false
          }
        </Formik>
      </SettingsCard>
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.accountSettings.logoutLabel" />
            <LoadingButton danger onClick={() => logout()}>
              <FormattedMessage id="settings.accountSettings.logoutText" />
            </LoadingButton>
          </Header>
        }
      />
    </>
  );
};

export { AccountSettingsView };
