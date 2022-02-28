import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExclamationCircle } from "@fortawesome/free-solid-svg-icons";

import { ReleaseStage } from "core/domain/connector";

const Content = styled.div`
  display: flex;
  flex-direction: row;
  padding: 13px 20px;
  border: 1px solid ${({ theme }) => theme.redColor};
  border-radius: 8px;
  font-size: 12px;
  line-height: 18px;
  white-space: break-spaces;
  margin-top: 16px;
`;

const Exclamation = styled(FontAwesomeIcon)`
  font-size: 20px;
  margin-right: 12px;
  color: ${({ theme }) => theme.redColor};
`;

type WarningMessageProps = {
  stage: ReleaseStage.ALPHA | ReleaseStage.BETA;
};

const WarningMessage: React.FC<WarningMessageProps> = ({ stage }) => {
  return (
    <Content>
      <Exclamation icon={faExclamationCircle} />
      <div>
        <FormattedMessage id={`connector.connectorsInDevelopment.${stage}`} />
      </div>
    </Content>
  );
};

export { WarningMessage };
