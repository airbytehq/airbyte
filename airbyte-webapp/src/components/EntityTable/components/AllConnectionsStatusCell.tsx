import React, { useMemo } from "react";

import { Status } from "../types";
import StatusIcon from "components/StatusIcon";

type AllConnectionsStatusCellProps = {
  connectEntities: {
    name: string;
    connector: string;
    status: string;
  }[];
};

const AllConnectionsStatusCell: React.FC<AllConnectionsStatusCellProps> = ({
  connectEntities,
}) => {
  const active = useMemo(
    () => connectEntities.filter((entity) => entity.status === Status.ACTIVE),
    [connectEntities]
  );

  const inactive = useMemo(
    () => connectEntities.filter((entity) => entity.status === Status.INACTIVE),
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
    </>
  );
};

export default AllConnectionsStatusCell;
