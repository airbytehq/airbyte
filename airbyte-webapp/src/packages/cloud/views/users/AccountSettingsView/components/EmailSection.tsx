import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import { useMutation } from "react-query";
import styled from "styled-components";

import { Button } from "components";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { GoogleAuthService } from "packages/cloud/lib/auth/GoogleAuthService";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";
import NotificationsForm from "pages/SettingsPage/pages/NotificationPage/components/NotificationsForm";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import useWorkspace from "hooks/services/useWorkspace";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";
import { useAuth } from "packages/firebaseReact";
import { useGetUserService } from "../../../../services/users/UserService";

const ChangeEmailFooter = styled.div`
  display: flex;
  align-items: center;
  height: 50px;
`;

export const EmailSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const user = useCurrentUser();
  const userService = useGetUserService();
  const auth = useAuth();
  const authService = useMemo(() => new GoogleAuthService(() => auth), []);

  const { workspace } = useWorkspace();
  const {
    errorMessage,
    successMessage,
    loading,
    updateData,
  } = useWorkspaceEditor();

  const { isLoading: isChangingEmail, mutate: changeEmail } = useMutation<
    void,
    Error,
    string
  >(async (email) => {
    await authService.changeEmail(email);
    return userService.changeEmail(email);
  });

  const onChange = async (data: {
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateData({ ...workspace, ...data });
  };
  return (
    <SettingsCard>
      <Content>
        <Formik
          initialValues={{
            email: user.email,
          }}
          onSubmit={(v) => {
            changeEmail(v.email);
          }}
        >
          {() => (
            <Form>
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
              <ChangeEmailFooter>
                <Button isLoading={isChangingEmail} type="submit">
                  save
                </Button>
              </ChangeEmailFooter>
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};
