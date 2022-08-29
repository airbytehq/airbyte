import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, H4, StatusIcon } from "components";

import styles from "./TryAfterErrorBlock.module.scss";

const Block = styled.div`
  padding: 40px;
  text-align: center;
`;
const Title = styled(H4)`
  padding: 16px 0 10px;
`;
interface TryAfterErrorBlockProps {
  message?: React.ReactNode;
  onClick: () => void;
  additionControl?: React.ReactNode;
}

const TryAfterErrorBlock: React.FC<TryAfterErrorBlockProps> = ({ message, onClick }) => (
  <Block>
    <StatusIcon big />
    <Title center>{message || <FormattedMessage id="form.schemaFailed" />}</Title>
    <Button customStyle={styles.againButton} onClick={onClick} variant="danger">
      <FormattedMessage id="form.tryAgain" />
    </Button>
  </Block>
);

export default TryAfterErrorBlock;
