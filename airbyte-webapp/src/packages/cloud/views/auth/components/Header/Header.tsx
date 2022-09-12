import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";

import useRouter from "hooks/useRouter";

import { CloudRoutes } from "../../../../cloudRoutes";
import styles from "./Header.module.scss";

interface HeaderProps {
  toLogin?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ toLogin }) => {
  const { push } = useRouter();
  return (
    <div className={styles.links}>
      <div className={styles.formLink}>
        <div className={styles.textBlock}>
          <FormattedMessage id={toLogin ? "login.haveAccount" : "login.DontHaveAccount"} />
        </div>
        <Button variant="secondary" onClick={() => push(toLogin ? CloudRoutes.Login : CloudRoutes.Signup)}>
          <FormattedMessage id={toLogin ? "login.login" : "login.signup"} />
        </Button>
      </div>
    </div>
  );
};
