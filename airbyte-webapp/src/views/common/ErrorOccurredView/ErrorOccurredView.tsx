import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";

import styles from "./ErrorOccurredView.module.scss";

interface ErrorOccurredViewProps {
  message: React.ReactNode;
  /**
   * URL to relevant documentation for the error if available
   */
  docLink?: string;
  ctaButtonText?: React.ReactNode;
  onCtaButtonClick?: React.MouseEventHandler;
}

export const ErrorOccurredView: React.FC<ErrorOccurredViewProps> = ({
  message,
  onCtaButtonClick,
  ctaButtonText,
  docLink,
}) => {
  return (
    <div className={styles.errorOccurredView} data-testid="errorView">
      <div className={styles.content}>
        <img src="/images/octavia/biting-nails.png" alt="" className={styles.octavia} />
        <Heading as="h2" size="lg" centered>
          <FormattedMessage id="errorView.title" />
        </Heading>
        <p className={styles.message}>{message}</p>
        {docLink && (
          <p>
            <a href={docLink} target="_blank" rel="noreferrer">
              <FormattedMessage id="errorView.docLink" />
            </a>
          </p>
        )}
        {onCtaButtonClick && ctaButtonText && (
          <Button size="lg" onClick={onCtaButtonClick}>
            {ctaButtonText}
          </Button>
        )}
      </div>
    </div>
  );
};
