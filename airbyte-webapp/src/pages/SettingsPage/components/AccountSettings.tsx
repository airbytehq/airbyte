import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard, PreferencesForm } from "components";
import useWorkspace from "components/hooks/services/useWorkspaceHook";
import WebHookForm from "./WebHookForm";

const SettingsCard = styled(ContentCard)`
  max-width: 638px;
  width: 100%;
  margin-top: 12px;

  &:first-child {
    margin-top: 0;
  }
`;

const Content = styled.div`
  padding: 27px 26px 15px;
`;

const AccountSettings: React.FC = () => {
  const {
    workspace,
    updatePreferences,
    updateWebhook,
    testWebhook,
  } = useWorkspace();
  const [errorMessage, setErrorMessage] = useState<React.ReactNode>(null);
  const [successMessage, setSuccessMessage] = useState<React.ReactNode>(null);
  const [
    errorWebhookMessage,
    setErrorWebhookMessage,
  ] = useState<React.ReactNode>(null);
  const [
    successWebhookMessage,
    setSuccessWebhookMessage,
  ] = useState<React.ReactNode>(null);

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await updatePreferences(data);
      setSuccessMessage(<FormattedMessage id="form.changesSaved" />);
    } catch (e) {
      setErrorMessage(<FormattedMessage id="form.someError" />);
    }
  };

  const onSubmitWebhook = async (data: { webhook: string }) => {
    setSuccessWebhookMessage(null);
    setErrorWebhookMessage(null);
    try {
      await updateWebhook(data);
      setSuccessWebhookMessage(<FormattedMessage id="settings.changeSaved" />);

      setTimeout(() => {
        setSuccessWebhookMessage(null);
      }, 2000);
    } catch (e) {
      setErrorWebhookMessage(<FormattedMessage id="form.someError" />);

      setTimeout(() => {
        setErrorWebhookMessage(null);
      }, 2000);
    }
  };

  const onTestWebhook = async (data: { webhook: string }) => {
    await testWebhook(data.webhook);
  };

  const initialWebhookUrl =
    workspace.notifications && workspace.notifications.length
      ? workspace.notifications[0].slackConfiguration.webhook
      : "";

  return (
    <>
      <SettingsCard title={<FormattedMessage id="settings.webhook" />}>
        <Content>
          <WebHookForm
            notificationUrl={initialWebhookUrl}
            onSubmit={onSubmitWebhook}
            onTest={onTestWebhook}
            errorMessage={errorWebhookMessage}
            successMessage={successWebhookMessage}
          />
        </Content>
      </SettingsCard>
      <SettingsCard title={<FormattedMessage id="settings.accountSettings" />}>
        <Content>
          <PreferencesForm
            errorMessage={errorMessage}
            successMessage={successMessage}
            onSubmit={onSubmit}
            isEdit
            preferencesValues={{
              email: workspace.email,
              anonymousDataCollection: workspace.anonymousDataCollection,
              news: workspace.news,
              securityUpdates: workspace.securityUpdates,
            }}
          />
        </Content>
      </SettingsCard>
    </>
  );
};

export default AccountSettings;
