import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Tooltip } from "components/base/Tooltip";
import StatusIcon from "components/StatusIcon";
import { StatusIconStatus } from "components/StatusIcon/StatusIcon";

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
    <Tooltip
      control={<StatusIcon {...statusIconProps} title={formatMessage({ id: statusIconProps.title })} />}
      placement="top"
    >
      {/* {description} */}
      <FormattedMessage id={statusIconProps.title} />
    </Tooltip>
  ) : null;
};

export default AllConnectionsStatusCell;
