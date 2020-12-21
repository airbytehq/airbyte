import React, { useContext, useEffect } from "react";
import ChatWidget from "@papercups-io/chat-widget";
import { Storytime } from "@papercups-io/storytime";
import { ThemeContext } from "styled-components";

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

  const theme = useContext(ThemeContext);

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
