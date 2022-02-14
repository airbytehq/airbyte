import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

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

const Sign = styled.img`
  height: 20px;
  width: 20px;
  min-width: 20px;
  margin-right: 12px;
  display: inline-block;
`;

const WarningMessage: React.FC = () => {
  return (
    <Content>
      <Sign src="/exclamationPoint.svg" />
      <div>
        <FormattedMessage
          id="connector.connectorsInDevelopment"
          values={{
            b: (...b: React.ReactNode[]) => <strong>{b}</strong>,
          }}
        />
      </div>
    </Content>
  );
};

export default WarningMessage;
