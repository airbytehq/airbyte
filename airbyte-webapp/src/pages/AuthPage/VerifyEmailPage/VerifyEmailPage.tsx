import React, { useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { Link } from "components";
import MessageBox from "components/base/MessageBox";
import HeadTitle from "components/HeadTitle";

import { RoutePaths } from "pages/routePaths";

import { LogoIcon } from "./components/LogoIcon";
import styles from "./VerifyEmailPage.module.scss";

const VerifyEmailPage: React.FC = () => {
  const [message, setMessage] = useState<string>("");

  const onClose = useCallback(() => {
    setMessage("");
  }, []);

  return (
    <div className={styles.container}>
      <HeadTitle titles={[{ id: "verifyEmail.pageTitle" }]} />
      <div className={styles.header}>
        <LogoIcon />
        <div className={styles.rightPanel}>
          <span className={styles.hasAccountText}>
            <FormattedMessage id="signup.haveAccount" />
          </span>

          <button className={styles.button}>
            <Link $clear to={`/${RoutePaths.Signin}`}>
              <FormattedMessage id="signup.siginButton" />
            </Link>
          </button>
        </div>
      </div>
      <div className={styles.messageBox}>
        <MessageBox message={message} type="info" fixed={false} onClose={onClose} />
      </div>

      <div className={styles.bodyPanel}>
        <div className={styles.cardPanel}>
          <h3 className={styles.h3}>
            <FormattedMessage id="verifyEmail.title" />
          </h3>
          <span className={styles.text}>
            <FormattedMessage id="verifyEmail.text1" />
          </span>
          <p className={styles.text}>
            <FormattedMessage
              id="verifyEmail.text2"
              values={{
                resentText: (
                  <div className={styles.links}>
                    <FormattedMessage id="verifyEmail.resentText" />
                  </div>
                ),
                clickHereText: (
                  <Link to={`/${RoutePaths.Signin}`} className={styles.links}>
                    <FormattedMessage id="verifyEmail.clickHereText" />
                  </Link>
                ),
              }}
            />
          </p>
          <p className={styles.text}>
            <FormattedMessage
              id="verifyEmail.text3"
              values={{
                infoText: (
                  <a href="mailto:info@daspire.com" className={styles.links}>
                    <FormattedMessage id="verifyEmail.info" />
                  </a>
                ),
              }}
            />
          </p>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
