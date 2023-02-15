import React from "react";

import Indicator from "components/Indicator";

import { useGetConnectorsOutOfDate } from "hooks/services/useConnector";

import styles from "./NotificationIndicator.module.scss";

export const NotificationIndicator: React.FC = () => {
  const { hasNewVersions } = useGetConnectorsOutOfDate();

  return hasNewVersions ? <Indicator className={styles.notification} /> : null;
};
