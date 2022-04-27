import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { LabeledInput, LoadingButton } from "components";

import { useAuthService, useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { RowFieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import { EmailSection, PasswordSection } from "./components";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
`;

const AccountSettingsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { logout } = useAuthService();
  const user = useCurrentUser();

  return (
    <>
      <SettingsCard title={<FormattedMessage id="settings.account" />}>
        <Content>
          <Formik
            initialValues={{
              name: user.name,
            }}
            onSubmit={() => {
              throw new Error("Not implemented");
            }}
          >
            {() => (
              <Form>
                <RowFieldItem>
                  <Field name="name">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        label={<FormattedMessage id="settings.accountSettings.fullName" />}
                        disabled={true}
                        placeholder={formatMessage({
                          id: "settings.accountSettings.fullName.placeholder",
                        })}
                        type="text"
                        error={!!meta.error && meta.touched}
                        message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                      />
                    )}
                  </Field>
                </RowFieldItem>
              </Form>
            )}
          </Formik>
        </Content>
      </SettingsCard>
      <EmailSection />
      <PasswordSection />
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.accountSettings.logoutLabel" />
            <LoadingButton danger onClick={() => logout()} data-testid="button.signout">
              <FormattedMessage id="settings.accountSettings.logoutText" />
            </LoadingButton>
          </Header>
        }
      />
    </>
  );
};

export { AccountSettingsView };
