import React, { useEffect } from "react";
import ChatWidget from "@papercups-io/chat-widget";
import { Storytime } from "@papercups-io/storytime";
import { theme } from "../../theme";

type PapercupsConfig = {
  accountId: string;
  baseUrl: string;
  enableStorytime: boolean;
};

type IProps = {
  papercupsConfig: PapercupsConfig;
  customerId: string;
};

const SupportChat: React.FC<IProps> = ({ papercupsConfig, customerId }) => {
  useEffect(() => {
    if (papercupsConfig.enableStorytime) {
      Storytime.init({
        accountId: papercupsConfig.accountId,
        baseUrl: papercupsConfig.baseUrl,
        customer: { external_id: customerId }
      });
    }
  }, [customerId, papercupsConfig]);

  return (
    <ChatWidget
      title="Welcome to Airbyte"
      subtitle="Ask us anything in the chat window below 😊"
      primaryColor={theme.primaryColor}
      greeting="Hello!!!"
      newMessagePlaceholder="Start typing..."
      customer={{ external_id: customerId }}
      accountId={papercupsConfig.accountId}
      baseUrl={papercupsConfig.baseUrl}
    />
  );
};

export default SupportChat;
