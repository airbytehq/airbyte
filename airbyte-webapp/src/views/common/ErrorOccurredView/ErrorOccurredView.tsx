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
        <img src="/images/octavia/biting-nails.png" alt="" className={styles.octavia} />
        <H2 center>
          <FormattedMessage id="errorView.title" />
        </H2>
        <p className={styles.message}>{message}</p>
        {onCtaButtonClick && ctaButtonText && (
          <Button size="xl" onClick={onCtaButtonClick}>
            {ctaButtonText}
          </Button>
        )}
      </div>
    </div>
  );
};
