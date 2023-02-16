import React, { useMemo } from "react";
import { useIntl } from "react-intl";

import { StatusIcon } from "components/ui/StatusIcon";
import { StatusIconStatus } from "components/ui/StatusIcon/StatusIcon";

import styles from "./ConnectionStatusCell.module.scss";
import { EntityNameCell } from "./EntityNameCell";
import { Status } from "../types";

interface ConnectionStatusCellProps {
  status: string | null;
  value: string;
  enabled: boolean;
}

export const ConnectionStatusCell: React.FC<ConnectionStatusCellProps> = ({ status, value, enabled }) => {
  const { formatMessage } = useIntl();
  const statusIconStatus = useMemo<StatusIconStatus | undefined>(
    () =>
      status === Status.EMPTY
        ? "sleep"
        : status === Status.ACTIVE
        ? "success"
        : status === Status.INACTIVE
        ? "inactive"
        : status === Status.PENDING
        ? "loading"
        : status === Status.CANCELLED
        ? "cancelled"
        : undefined,
    [status]
  );
  const title =
    status === Status.EMPTY
      ? formatMessage({
          id: "connection.noSyncData",
        })
      : status === Status.INACTIVE
      ? formatMessage({
          id: "connection.disabledConnection",
        })
      : status === Status.ACTIVE
      ? formatMessage({
          id: "connection.successSync",
        })
      : status === Status.PENDING
      ? formatMessage({
          id: "connection.pendingSync",
        })
      : formatMessage({
          id: "connection.failedSync",
        });

  return (
    <div className={styles.content}>
      <StatusIcon title={title} status={statusIconStatus} />
      <EntityNameCell className={styles.text} value={value} enabled={enabled} />
    </div>
  );
};
