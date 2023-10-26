import React from "react";

// import { ImplementationTable } from "components/EntityTable";
// import { EntityTableDataItem } from "components/EntityTable/types";
// import { getEntityTableData } from "components/EntityTable/utils";

import DestinationTable from "components/EntityTable/DestinationTable";

import { DestinationRead } from "core/request/AirbyteClient";
// import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
// import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

interface DestinationsTableProps {
  destinations: DestinationRead[];
  // connections: WebBackendConnectionRead[];
}

const DestinationsTable: React.FC<DestinationsTableProps> = ({ destinations }) => {
  const { push } = useRouter();
  // const { connections } = useConnectionList();
  // const { destinationDefinitions } = useDestinationDefinitionList();

  // const data = getEntityTableData(destinations, connections, destinationDefinitions, "destination");

  const clickRow = (destination: DestinationRead) => push(`${destination.destinationId}`);

  return <DestinationTable data={destinations} onClickRow={clickRow} entity="destination" />;
};

export default DestinationsTable;
