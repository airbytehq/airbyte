import React from "react";
import styled from "styled-components";

import Indicator from "components/Indicator";

import useConnector from "hooks/services/useConnector";

const Notification = styled(Indicator)`
  position: absolute;
  top: 11px;
  right: 23px;
`;

export const NotificationIndicator: React.FC = () => {
  const { hasNewVersions } = useConnector();

  return hasNewVersions ? <Notification /> : null;
};
