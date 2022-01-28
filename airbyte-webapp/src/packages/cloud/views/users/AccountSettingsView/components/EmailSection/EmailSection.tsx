import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import styled from "styled-components";

import { Button } from "components";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";
import NotificationsForm from "pages/SettingsPage/pages/NotificationPage/components/NotificationsForm";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import useWorkspace from "hooks/services/useWorkspace";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";

import { FormValues } from "./typings";
import { useEmail } from "./hooks";

const ChangeEmailFooter = styled.div`
  display: flex;
  align-items: center;
  height: 50px;
`;

const TextInputsSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const EmailSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const user = useCurrentUser();

  const emailService = useEmail();

  const { workspace } = useWorkspace();
  const { errorMessage, successMessage, loading, updateData } =
    useWorkspaceEditor();

  const onChange = async (data: {
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateData({ ...workspace, ...data });
  };

  return (
    <SettingsCard>
      <Content>
        <Formik<FormValues>
          initialValues={{
            email: user.email,
            password: "",
          }}
          onSubmit={emailService.updateEmail}
        >
          {({ values }) => (
            <Form>
              <FieldItem>
                <TextInputsSection>
                  <Field name="email">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        disabled
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

                  {user.email !== values.email && (
                    <Field name="password">
                      {({ field, meta }: FieldProps<string>) => (
                        <LabeledInput
                          {...field}
                          label={
                            <FormattedMessage id="settings.accountSettings.enterPassword" />
                          }
                          placeholder=""
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
                  )}
                </TextInputsSection>
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
              <ChangeEmailFooter style={{ display: "none" }}>
                <Button type="submit" disabled={user.email === values.email}>
                  <FormattedMessage id="settings.accountSettings.updateEmail" />
                </Button>
              </ChangeEmailFooter>
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};

export default EmailSection;
