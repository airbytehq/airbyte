import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

type RequestConnectorBlockProps = {
  onClick: () => void;
};

const Block = styled.div`
  cursor: pointer;
  color: ${({ theme }) => theme.textColor};

  &:hover {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const RequestConnectorBlock: React.FC<RequestConnectorBlockProps> = ({
  onClick,
}) => {
  return (
    <Block onClick={onClick}>
      <FormattedMessage id="connector.requestConnectorBlock" />
    </Block>
  );
};

export default RequestConnectorBlock;
