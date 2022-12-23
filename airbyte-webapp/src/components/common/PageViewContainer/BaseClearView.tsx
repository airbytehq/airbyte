import React from "react";
import { useIntl } from "react-intl";
import { Link } from "react-router-dom";

import { Version } from "../Version";
import styles from "./BaseClearView.module.scss";

export const BaseClearView: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();
  return (
    <div className={styles.content}>
      <div className={styles.mainInfo}>
        <Link to="..">
          <img className={styles.logoImg} src="/logo.png" alt={formatMessage({ id: "ui.goBack" })} />
        </Link>
        {children}
      </div>
      <Version />
    </div>
  );
};
