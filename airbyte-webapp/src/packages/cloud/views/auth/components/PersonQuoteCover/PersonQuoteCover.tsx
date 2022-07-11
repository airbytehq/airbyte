import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./PersonQuoteCover.module.scss";

export interface PersonQuoteCoverProps {
  overlayGradientStyle?: React.CSSProperties;
  backgroundImageStyle?: React.CSSProperties;
  quoteText?: string;
  quoteTextStyle?: React.CSSProperties;
  logoImageSrc?: string;
  quoteAuthorFullNameStyle?: React.CSSProperties;
  quoteAuthorJobTitleStyle?: React.CSSProperties;
}
export const PersonQuoteCover: React.FC<PersonQuoteCoverProps> = ({
  backgroundImageStyle,
  overlayGradientStyle,
  quoteText,
  quoteTextStyle,
  logoImageSrc,
  quoteAuthorFullNameStyle,
  quoteAuthorJobTitleStyle,
}) => {
  return (
    <div className={styles.container}>
      <div className={styles.image} style={backgroundImageStyle} data-testid="background-image" />
      <div className={styles.overlay} style={overlayGradientStyle} data-testid="gradient-overlay" />
      <div className={styles.contentContainer}>
        <blockquote className={styles.quote} style={quoteTextStyle} data-testid="quote">
          <p>{quoteText ? quoteText : <FormattedMessage id="login.quoteText" />}</p>
        </blockquote>
        <img
          src={logoImageSrc ? logoImageSrc : "/images/testimonials/cartdotcom-logo.svg"}
          className={styles.companyLogo}
          alt=""
          data-testid="quote-company-logo"
        />
        <div>
          <h5
            className={styles.quoteAuthorFullName}
            style={quoteAuthorFullNameStyle}
            data-testid="quote-author-full-name"
          >
            <FormattedMessage id="login.quoteAuthor" />
          </h5>
          <h3
            className={styles.quoteAuthorJobTitle}
            style={quoteAuthorJobTitleStyle}
            data-testid="quote-author-job-title"
          >
            <FormattedMessage id="login.quoteAuthorJobTitle" />
          </h3>
        </div>
      </div>
    </div>
  );
};
