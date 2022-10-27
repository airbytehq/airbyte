import React from "react";
import { FormattedMessage } from "react-intl";

import { StatusIcon } from "components/StatusIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import styles from "./TryAfterErrorBlock.module.scss";

interface TryAfterErrorBlockProps {
  message?: string;
  onClick: () => void;
}

export const TryAfterErrorBlock: React.FC<TryAfterErrorBlockProps> = ({ message, onClick }) => {
  return (
    <div className={styles.container}>
      <StatusIcon big />
      <Text as="p" size="lg" centered className={styles.message}>
        <FormattedMessage id="form.schemaFailed" />
      </Text>
      {message && (
        <Text as="p" size="lg" centered className={styles.message}>
          <FormattedMessage id="form.error" values={{ message }} />
        </Text>
      )}
      <Button className={styles.retryButton} onClick={onClick} variant="danger">
        <FormattedMessage id="form.tryAgain" />
      </Button>
    </div>
  );
};
