import React, { PropsWithChildren } from "react";
import { useIntl } from "react-intl";
import { Link } from "react-router-dom";

import { RoutePaths } from "pages/routePaths";

import styles from "./AirbyteHomeLink.module.scss";
import { ReactComponent as AirbyteLogo } from "./airbyteLogo.svg";

export const AirbyteHomeLink: React.FC<PropsWithChildren<unknown>> = () => {
  const { formatMessage } = useIntl();

  return (
    <Link to={RoutePaths.Connections} aria-label={formatMessage({ id: "sidebar.homepage" })}>
      <AirbyteLogo height={33} width={33} className={styles.logo} />
    </Link>
  );
};
