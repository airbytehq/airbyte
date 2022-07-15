import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./PersonQuoteCover.module.scss";

export const PersonQuoteCover: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.image} data-testid="background-image" />
      <div className={styles.overlay} data-testid="gradient-overlay" />
      <div className={styles.contentContainer}>
        <blockquote className={styles.quote} data-testid="quote">
          <p>
            <FormattedMessage id="login.quoteText" />
          </p>
        </blockquote>
        <img
          src="/images/testimonials/cartdotcom-logo.svg"
          className={styles.companyLogo}
          alt=""
          data-testid="quote-company-logo"
        />
        <div>
          <h5 className={styles.quoteAuthorFullName} data-testid="quote-author-full-name">
            <FormattedMessage id="login.quoteAuthor" />
          </h5>
          <h3 className={styles.quoteAuthorJobTitle} data-testid="quote-author-job-title">
            <FormattedMessage id="login.quoteAuthorJobTitle" />
          </h3>
        </div>
      </div>
    </div>
  );
};
