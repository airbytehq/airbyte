import React, { useMemo } from "react";

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

  // TODO: add error status

  if (!connectEntities.length) {
    return null;
  }

  return (
    <>
      {active.length ? <StatusIcon success value={active.length} /> : null}
      {inactive.length ? <StatusIcon inactive value={inactive.length} /> : null}
      {failed.length ? <StatusIcon value={failed.length} /> : null}
      {empty.length ? <StatusIcon empty value={empty.length} /> : null}
    </>
  );
};

export default AllConnectionsStatusCell;
