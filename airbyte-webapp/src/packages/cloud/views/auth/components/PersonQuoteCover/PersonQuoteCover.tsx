import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./PersonQuoteCover.module.scss";

interface PersonQuoteCoverProps {
  overlayGradientStyle?: React.CSSProperties;
  backgroundImageStyle?: React.CSSProperties;
  quoteText?: string;
  quoteTextStyle?: React.CSSProperties;
  logoImageSrc?: string;
  quoteAuthorFullName?: string;
  quoteAuthorFullNameStyle?: React.CSSProperties;
  quoteAuthorJobTitle?: string;
  quoteAuthorJobTitleStyle?: React.CSSProperties;
}
export const PersonQuoteCover: React.FC<PersonQuoteCoverProps> = ({
  backgroundImageStyle,
  overlayGradientStyle,
  quoteText,
  quoteTextStyle,
  logoImageSrc,
  quoteAuthorFullName,
  quoteAuthorFullNameStyle,
  quoteAuthorJobTitle,
  quoteAuthorJobTitleStyle,
}) => {
  return (
    <div className={styles.image} style={backgroundImageStyle}>
      <div className={styles.overlay} style={overlayGradientStyle} />
      <div className={styles.container}>
        <blockquote className={styles.quote} style={quoteTextStyle}>
          <p>{quoteText ? quoteText : <FormattedMessage id="login.quoteText" />}</p>
        </blockquote>
        <img
          src={logoImageSrc ? logoImageSrc : "/cart-com-company-logo.svg"}
          className={styles.companyLogo}
          alt="company logo"
        />
        <div>
          <h5 className={styles.quoteAuthorFullName} style={quoteAuthorFullNameStyle}>
            {quoteAuthorFullName ? quoteAuthorFullName : <FormattedMessage id="login.quoteAuthor" />}
          </h5>
          <h3 className={styles.quoteAuthorJobTitle} style={quoteAuthorJobTitleStyle}>
            {quoteAuthorJobTitle ? quoteAuthorJobTitle : <FormattedMessage id="login.quoteAuthorJobTitle" />}
          </h3>
        </div>
      </div>
    </div>
  );
};
