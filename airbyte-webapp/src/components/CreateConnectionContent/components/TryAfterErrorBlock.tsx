import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button, H4, StatusIcon } from "components";

const Block = styled.div`
  margin: 40px;
  text-align: center;
`;
const Title = styled(H4)`
  padding: 16px 0 10px;
`;

const AgainButton = styled(Button)`
  min-width: 239px;
`;

type TryAfterErrorBlockProps = {
  message?: React.ReactNode;
  onClick: () => void;
  additionControl?: React.ReactNode;
};

const TryAfterErrorBlock: React.FC<TryAfterErrorBlockProps> = ({
  message,
  onClick,
}) => (
  <Block>
    <StatusIcon success={false} big />
    <Title center>
      {message || <FormattedMessage id="form.schemaFailed" />}
    </Title>
    <AgainButton onClick={onClick} danger>
      <FormattedMessage id="form.tryAgain" />
    </AgainButton>
  </Block>
);

export default TryAfterErrorBlock;
