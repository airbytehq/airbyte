import React from "react";
import { FormattedMessage } from "react-intl";

import { StatusIcon } from "components/StatusIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import styles from "./TryAfterErrorBlock.module.scss";

interface TryAfterErrorBlockProps {
  message?: React.ReactNode;
  onClick: () => void;
}

export const TryAfterErrorBlock: React.FC<TryAfterErrorBlockProps> = ({ message, onClick }) => (
  <div className={styles.container}>
    <StatusIcon big />
    <Text as="p" size="lg" centered className={styles.message}>
      {message || <FormattedMessage id="form.schemaFailed" />}
    </Text>
    <Button className={styles.retryButton} onClick={onClick} variant="danger">
      <FormattedMessage id="form.tryAgain" />
    </Button>
  </div>
);
