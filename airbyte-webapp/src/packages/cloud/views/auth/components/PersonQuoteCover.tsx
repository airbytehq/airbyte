import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./PersonQuoteCover.module.scss";

interface PersonQuoteCoverProps {
  isBackgroundImageShown?: boolean;
  backgroundImage?: string;
  quoteText?: string;
  logoImage?: string;
  quoteAuthorFullName?: string;
  quoteAuthorJobTitle?: string;
}
export const PersonQuoteCover: React.FC<PersonQuoteCoverProps> = ({
  isBackgroundImageShown,
  backgroundImage,
  quoteText,
  logoImage,
  quoteAuthorFullName,
  quoteAuthorJobTitle,
}) => {
  return (
    <div className={styles.overlay}>
      <div
        className={styles.imageContainer}
        style={{
          backgroundImage: `url(
            ${isBackgroundImageShown && backgroundImage}
          )`,
        }}
      />
      <div className={styles.blockQuote}>
        <blockquote className={styles.quote}>
          <p>{quoteText ? quoteText : <FormattedMessage id="login.quoteText" />}</p>
        </blockquote>
        <img src={logoImage} className={styles.companyLogo} alt="company logo" />
        <div>
          <h5 className={styles.quoteAuthorFullName}>
            {quoteAuthorFullName ? quoteAuthorFullName : <FormattedMessage id="login.quoteAuthor" />}
          </h5>
          <h3 className={styles.quoteAuthorJobTitle}>
            {quoteAuthorJobTitle ? quoteAuthorJobTitle : <FormattedMessage id="login.quoteAuthorJobTitle" />}
          </h3>
        </div>
      </div>
    </div>
  );
};

PersonQuoteCover.defaultProps = {
  isBackgroundImageShown: true,
  backgroundImage: "/person-photo.png",
  logoImage: "/cart-com-company-logo.svg",
};
