import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import styled from "styled-components";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { LabeledInput, LoadingButton } from "components";
import {
  useAuthService,
  useCurrentUser,
} from "packages/cloud/services/auth/AuthService";
import {
  FieldItem,
  RowFieldItem,
} from "packages/cloud/views/auth/components/FormComponents";
import NotificationsForm from "pages/SettingsPage/pages/NotificationPage/components/NotificationsForm";
import useWorkspace from "hooks/services/useWorkspace";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
`;

const AccountSettingsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { logout } = useAuthService();
  const user = useCurrentUser();

  const { workspace } = useWorkspace();
  const {
    errorMessage,
    successMessage,
    loading,
    updateData,
  } = useWorkspaceEditor();

  const onChange = async (data: {
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateData({ ...workspace, ...data });
  };

  return (
    <>
      <SettingsCard title={<FormattedMessage id="settings.account" />}>
        <Content>
          <Formik
            initialValues={{
              firstName: "",
              lastName: "",
              email: user.email,
              password: "",
            }}
            onSubmit={() => {
              throw new Error("Not implemented");
            }}
          >
            {() => (
              <Form>
                <RowFieldItem>
                  <Field name="firstName">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        label={
                          <FormattedMessage id="settings.accountSettings.firstName" />
                        }
                        placeholder={formatMessage({
                          id: "settings.accountSettings.firstName.placeholder",
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
                          <FormattedMessage id="settings.accountSettings.lastName" />
                        }
                        placeholder={formatMessage({
                          id: "settings.accountSettings.lastName.placeholder",
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
                </RowFieldItem>
                <FieldItem>
                  <Field name="email">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        label={
                          <FormattedMessage id="settings.accountSettings.email" />
                        }
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
                <FieldItem>
                  <Field name="password">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        label={
                          <FormattedMessage id="settings.accountSettings.password" />
                        }
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
          <NotificationsForm
            isLoading={loading}
            errorMessage={errorMessage}
            successMessage={successMessage}
            onChange={onChange}
            preferencesValues={{
              news: workspace.news,
              securityUpdates: workspace.securityUpdates,
            }}
          />
        </Content>
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
