import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button } from "components/ui/Button";

import { CloudRoutes } from "packages/cloud/cloudRoutePaths";

import styles from "./Header.module.scss";

interface HeaderProps {
  toLogin?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ toLogin }) => {
  const navigate = useNavigate();
  return (
    <div className={styles.links}>
      <div className={styles.formLink}>
        <div className={styles.textBlock}>
          <FormattedMessage id={toLogin ? "login.haveAccount" : "login.DontHaveAccount"} />
        </div>
        <Button variant="secondary" onClick={() => navigate(toLogin ? CloudRoutes.Login : CloudRoutes.Signup)}>
          <FormattedMessage id={toLogin ? "login.login" : "login.signup"} />
        </Button>
      </div>
    </div>
  );
};
