import React from "react";
import { useIntl } from "react-intl";

import { Link } from "components/ui/Link";

import { RoutePaths } from "pages/routePaths";

import styles from "./AirbyteHomeLink.module.scss";
import { ReactComponent as AirbyteLogo } from "./airbyteLogo.svg";

export const AirbyteHomeLink: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Link to={RoutePaths.Connections} aria-label={formatMessage({ id: "sidebar.homepage" })}>
      <AirbyteLogo height={33} width={33} className={styles.logo} />
    </Link>
  );
};
