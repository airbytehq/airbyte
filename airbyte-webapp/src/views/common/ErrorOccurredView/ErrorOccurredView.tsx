import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, H2 } from "components";

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
        <H2 center className={styles.h2}>
          <FormattedMessage id="errorView.title" />
        </H2>
        <img src="/images/octavia/over-error.png" alt="" className={styles.octavia} />
        <p className={styles.message}>{message}</p>
        <p className={styles.tips}>
          <FormattedMessage id="onboarding.tryAgainText" />
        </p>
        {onCtaButtonClick && ctaButtonText && (
          <Button size="xl" onClick={onCtaButtonClick}>
            {ctaButtonText}
          </Button>
        )}
      </div>
    </div>
  );
};
