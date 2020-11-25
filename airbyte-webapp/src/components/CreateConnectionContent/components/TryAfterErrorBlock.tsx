import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "../../Button";
import { H4 } from "../../Titles";
import StatusIcon from "../../StatusIcon";

const Block = styled.div`
  margin: 40px;
  text-align: center;
`;
const Title = styled(H4)`
  padding: 16px 0 10px;
`;

type IProps = {
  message?: React.ReactNode;
  onClick: () => void;
};

const TryAfterErrorBlock: React.FC<IProps> = ({ message, onClick }) => {
  return (
    <Block>
      <StatusIcon success={false} big />
      <Title center>
        {message || <FormattedMessage id="form.schemaFailed" />}
      </Title>
      <Button onClick={onClick} danger>
        <FormattedMessage id="form.tryAgain" />
      </Button>
    </Block>
  );
};

export default TryAfterErrorBlock;
