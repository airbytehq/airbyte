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
  setSortFieldName?: any;
  setSortDirection?: any;
  onSelectFilter?: any;
  localSortOrder?: any;
  setLocalSortOrder?: any;
  destinationSortOrder?: any;
  setDestinationSortOrder?: any;
  pageCurrent?: any;
  pageSize?: any;

  // connections: WebBackendConnectionRead[];
}

const DestinationsTable: React.FC<DestinationsTableProps> = ({
  destinations,
  setSortDirection,
  setSortFieldName,
  onSelectFilter,
  localSortOrder,
  setLocalSortOrder,
  destinationSortOrder,
  setDestinationSortOrder,
  pageCurrent,
  pageSize,
  // pageCurrent
}) => {
  const { push } = useRouter();
  // const { connections } = useConnectionList();
  // const { destinationDefinitions } = useDestinationDefinitionList();

  // const data = getEntityTableData(destinations, connections, destinationDefinitions, "destination");

  const clickRow = (destination: DestinationRead) => push(`${destination.destinationId}`);

  return (
    <DestinationTable
      data={destinations}
      onClickRow={clickRow}
      entity="destination"
      setSortFieldName={setSortFieldName}
      setSortDirection={setSortDirection}
      onSelectFilter={onSelectFilter}
      localSortOrder={localSortOrder}
      setLocalSortOrder={setLocalSortOrder}
      destinationSortOrder={destinationSortOrder}
      setDestinationSortOrder={setDestinationSortOrder}
      pageCurrent={pageCurrent}
      pageSize={pageSize}
    />
  );
};

export default DestinationsTable;
