import React, { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
import useWorkspace from "hooks/services/useWorkspace";
import WebHookForm from "./components/WebHookForm";
import HeadTitle from "components/HeadTitle";

import { Content, SettingsCard } from "../SettingsComponents";

function useAsyncWithTimeout<K, T>(f: (data: K) => Promise<T>) {
  const [errorMessage, setErrorMessage] = useState<React.ReactNode>(null);
  const [successMessage, setSuccessMessage] = useState<React.ReactNode>(null);
  const call = useCallback(
    async (data: K) => {
      setSuccessMessage(null);
      setErrorMessage(null);
      try {
        await f(data);
        setSuccessMessage(<FormattedMessage id="settings.changeSaved" />);

        setTimeout(() => {
          setSuccessMessage(null);
        }, 2000);
      } catch (e) {
        setErrorMessage(<FormattedMessage id="form.someError" />);

        setTimeout(() => {
          setErrorMessage(null);
        }, 2000);
      }
    },
    [f]
  );

  return {
    call,
    successMessage,
    errorMessage,
  };
}

const NotificationPage: React.FC = () => {
  const { workspace, updateWebhook, testWebhook } = useWorkspace();

  const {
    call: onSubmitWebhook,
    errorMessage,
    successMessage,
  } = useAsyncWithTimeout(async (data: { webhook: string }) =>
    updateWebhook(data)
  );

  const onTestWebhook = async (data: { webhook: string }) => {
    await testWebhook(data.webhook);
  };

  const initialWebhookUrl = workspace.notifications?.length
    ? workspace.notifications[0].slackConfiguration.webhook
    : "";

  return (
    <>
      <HeadTitle
        titles={[{ id: "sidebar.settings" }, { id: "settings.notifications" }]}
      />
      <SettingsCard
        title={<FormattedMessage id="settings.notificationSettings" />}
      >
        <Content>
          <WebHookForm
            notificationUrl={initialWebhookUrl}
            onSubmit={onSubmitWebhook}
            onTest={onTestWebhook}
            errorMessage={errorMessage}
            successMessage={successMessage}
          />
        </Content>
      </SettingsCard>
    </>
  );
};

export default NotificationPage;
