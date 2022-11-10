import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";

import styles from "./ErrorOccurredView.module.scss";

interface ErrorOccurredViewProps {
  message: React.ReactNode;
  ctaButtonText?: React.ReactNode;
  onCtaButtonClick?: React.MouseEventHandler;
}

export const ErrorOccurredView: React.FC<ErrorOccurredViewProps> = ({ message, onCtaButtonClick, ctaButtonText }) => {
  return (
    <div className={styles.errorOccurredView}>
      <div className={styles.content}>
        <img src="/images/octavia/biting-nails.png" alt="" className={styles.octavia} />
        <Heading as="h2" size="lg" centered>
          <FormattedMessage id="errorView.title" />
        </Heading>
        <p className={styles.message}>{message}</p>
        {onCtaButtonClick && ctaButtonText && (
          <Button size="lg" onClick={onCtaButtonClick}>
            {ctaButtonText}
          </Button>
        )}
      </div>
    </div>
  );
};
