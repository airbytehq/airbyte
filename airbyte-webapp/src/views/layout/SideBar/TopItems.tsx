import React, { PropsWithChildren } from "react";
import { useIntl } from "react-intl";
import { Link } from "react-router-dom";

import { RoutePaths } from "pages/routePaths";

import { ReactComponent as AirbyteLogo } from "./airbyteLogo.svg";

export const TopItems: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();

  return (
    <div>
      <Link to={RoutePaths.Connections} aria-label={formatMessage({ id: "sidebar.homepage" })}>
        <AirbyteLogo height={33} width={33} />
      </Link>
      {children}
    </div>
  );
};
