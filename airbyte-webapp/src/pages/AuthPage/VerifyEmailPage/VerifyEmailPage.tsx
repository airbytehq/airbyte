import React, { useState, useCallback, useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { Link } from "components";
import MessageBox from "components/base/MessageBox";
import HeadTitle from "components/HeadTitle";

import { RoutePaths } from "pages/routePaths";

import { getRegisterUserToken, setRegisterUserDetails } from "../../../core/AuthContext";
import { RegisterUserDetails } from "../../../services/auth/AuthService";
import { useAuthenticationService } from "../../../services/auth/AuthSpecificationService";
import { LogoIcon } from "./components/LogoIcon";
import styles from "./VerifyEmailPage.module.scss";

const VerifyEmailPage: React.FC = () => {
  const signUp = useAuthenticationService();
  const registerUserToken = getRegisterUserToken();
  const [verificationToken, setVerificationToken] = useState<string>();
  const [message, setMessage] = useState<string>("");
  const [msgType, setMsgType] = useState<"info" | "error">("info");

  const onClose = useCallback(() => {
    setMessage("");
  }, []);

  useEffect(() => {
    if (registerUserToken) {
      setVerificationToken(registerUserToken);
    }
  }, [registerUserToken]);

  const setNotification = (msg: string, type: "info" | "error") => {
    setMessage(msg);
    setMsgType(type);
  };

  const onResendMail = useCallback(async (token: string) => {
    signUp
      .resendVerificationMail(token)
      .then((res: RegisterUserDetails) => {
        if (res.verificationToken !== null && res.verificationToken !== "") {
          setRegisterUserDetails(res);
          setNotification("verifyEmail.resend.success.message", "info");
        } else {
          setNotification("notifications.error.somethingWentWrong", "error");
        }
      })
      .catch((err: Error) => {
        setNotification(err.message, "error");
      });
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
        <MessageBox message={message} type={msgType} fixed={false} onClose={onClose} />
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
                  <Link to="" className={styles.links} onClick={() => onResendMail(verificationToken as string)}>
                    <FormattedMessage id="verifyEmail.resentText" />
                  </Link>
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
