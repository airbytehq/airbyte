import React, { useEffect } from "react";
import ChatWidget from "@papercups-io/chat-widget";
import { Storytime } from "@papercups-io/storytime";

type IProps = {
  accountId: string;
  baseUrl: string;
  customerId: string;
};

const SupportChat: React.FC<IProps> = ({ accountId, baseUrl, customerId }) => {
  useEffect(() => {
    Storytime.init({
      accountId: accountId,
      baseUrl: baseUrl,
      customer: { external_id: customerId }
    });
  }, [accountId, customerId, baseUrl]);

  return (
    <ChatWidget
      title="Welcome to Airbyte"
      subtitle="Ask us anything in the chat window below 😊"
      primaryColor="#625eff"
      greeting="Hello!!!"
      newMessagePlaceholder="Start typing..."
      customer={{ external_id: customerId }}
      accountId={accountId}
      baseUrl={baseUrl}
    />
  );
};

export default SupportChat;
