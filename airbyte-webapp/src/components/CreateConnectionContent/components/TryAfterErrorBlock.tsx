import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/base/Button";
import { Text } from "components/base/Text";
import { StatusIcon } from "components/StatusIcon";

import styles from "./TryAfterErrorBlock.module.scss";

interface TryAfterErrorBlockProps {
  message?: React.ReactNode;
  onClick: () => void;
}

const TryAfterErrorBlock: React.FC<TryAfterErrorBlockProps> = ({ message, onClick }) => (
  <div className={styles.container}>
    <StatusIcon big />
    <Text as="p" size="lg" centered className={styles.message}>
      {message || <FormattedMessage id="form.schemaFailed" />}
    </Text>
    <Button className={styles.retryButton} onClick={onClick} danger>
      <FormattedMessage id="form.tryAgain" />
    </Button>
  </div>
);

export default TryAfterErrorBlock;
