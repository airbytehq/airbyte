import React, { useMemo } from "react";
import { useIntl } from "react-intl";

import { StatusIcon } from "components/ui/StatusIcon";
import { StatusIconStatus } from "components/ui/StatusIcon/StatusIcon";

import { Status } from "../types";

const _statusConfig: Array<{ status: Status; statusIconStatus?: StatusIconStatus; titleId: string }> = [
  { status: Status.ACTIVE, statusIconStatus: "success", titleId: "connection.successSync" },
  { status: Status.INACTIVE, statusIconStatus: "inactive", titleId: "connection.disabledConnection" },
  { status: Status.FAILED, titleId: "connection.failedSync" },
  { status: Status.EMPTY, statusIconStatus: "sleep", titleId: "connection.noSyncData" },
];

interface AllConnectionStatusConnectEntity {
  name: string;
  connector: string;
  status: string;
  lastSyncStatus: string;
}

interface AllConnectionsStatusCellProps {
  connectEntities: AllConnectionStatusConnectEntity[];
}

const AllConnectionsStatusCell: React.FC<AllConnectionsStatusCellProps> = ({ connectEntities }) => {
  const { formatMessage } = useIntl();

  const statusIconProps = useMemo(() => {
    if (connectEntities.length) {
      for (const { status, statusIconStatus, titleId } of _statusConfig) {
        const filteredEntities = connectEntities.filter((entity) => entity.lastSyncStatus === status);
        if (filteredEntities.length) {
          return {
            status: statusIconStatus,
            value: filteredEntities.length,
            title: titleId,
          };
        }
      }
    }

    return undefined;
  }, [connectEntities]);

  return statusIconProps ? (
    <StatusIcon {...statusIconProps} title={formatMessage({ id: statusIconProps.title })} />
  ) : null;
};

export default AllConnectionsStatusCell;
