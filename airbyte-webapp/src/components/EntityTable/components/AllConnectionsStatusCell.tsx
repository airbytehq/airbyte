import React, { useMemo } from "react";
import { useIntl } from "react-intl";

import { Status } from "../types";
import StatusIcon from "components/StatusIcon";

type AllConnectionsStatusCellProps = {
  connectEntities: {
    name: string;
    connector: string;
    status: string;
    lastSyncStatus: string;
  }[];
};

const AllConnectionsStatusCell: React.FC<AllConnectionsStatusCellProps> = ({
  connectEntities,
}) => {
  const formatMessage = useIntl().formatMessage;

  const active = useMemo(
    () =>
      connectEntities.filter(
        (entity) => entity.lastSyncStatus === Status.ACTIVE
      ),
    [connectEntities]
  );

  const inactive = useMemo(
    () =>
      connectEntities.filter(
        (entity) => entity.lastSyncStatus === Status.INACTIVE
      ),
    [connectEntities]
  );

  const failed = useMemo(
    () =>
      connectEntities.filter(
        (entity) => entity.lastSyncStatus === Status.FAILED
      ),
    [connectEntities]
  );

  const empty = useMemo(
    () =>
      connectEntities.filter(
        (entity) => entity.lastSyncStatus === Status.EMPTY
      ),
    [connectEntities]
  );

  if (!connectEntities.length) {
    return null;
  }

  return (
    <>
      {active.length ? (
        <StatusIcon
          success
          value={active.length}
          title={formatMessage({
            id: "connection.successSync",
          })}
        />
      ) : null}
      {inactive.length ? (
        <StatusIcon
          inactive
          value={inactive.length}
          title={formatMessage({
            id: "connection.disabledConnection",
          })}
        />
      ) : null}
      {failed.length ? (
        <StatusIcon
          value={failed.length}
          title={formatMessage({
            id: "connection.failedSync",
          })}
        />
      ) : null}
      {empty.length ? (
        <StatusIcon
          empty
          value={empty.length}
          title={formatMessage({
            id: "connection.noSyncData",
          })}
        />
      ) : null}
    </>
  );
};

export default AllConnectionsStatusCell;
