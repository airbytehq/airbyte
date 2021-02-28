import React, { useEffect } from "react";
import { Storytime } from "@papercups-io/storytime";
import styled from "styled-components";
import { faComment } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import Button from "components/Button";

type PapercupsConfig = {
  accountId: string;
  baseUrl: string;
  enableStorytime: boolean;
};

type IProps = {
  papercupsConfig: PapercupsConfig;
  customerId: string;
  onClick?: () => void;
};

const ChatButton = styled(Button)`
  width: 50px;
  height: 50px;

  border-radius: 50%;
  padding: 0;

  position: fixed;
  bottom: 25px;
  right: 25px;

  font-size: 30px;
`;

const SupportChat: React.FC<IProps> = ({
  papercupsConfig,
  customerId,
  onClick,
}) => {
  useEffect(() => {
    if (papercupsConfig.enableStorytime) {
      Storytime.init({
        accountId: papercupsConfig.accountId,
        baseUrl: papercupsConfig.baseUrl,
        customer: { external_id: customerId },
      });
    }
  }, [customerId, papercupsConfig]);

  return (
    <ChatButton onClick={onClick}>
      <FontAwesomeIcon icon={faComment} />
    </ChatButton>
  );
};

export default SupportChat;
