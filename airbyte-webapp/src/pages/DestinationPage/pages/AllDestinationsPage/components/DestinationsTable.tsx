import React from "react";
import { useNavigate } from "react-router-dom";

import { ImplementationTable } from "components/EntityTable";
import { EntityTableDataItem } from "components/EntityTable/types";
import { getEntityTableData } from "components/EntityTable/utils";

import { DestinationRead } from "core/request/AirbyteClient";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

interface DestinationsTableProps {
  destinations: DestinationRead[];
}

const DestinationsTable: React.FC<DestinationsTableProps> = ({ destinations }) => {
  const navigate = useNavigate();
  const { connections } = useConnectionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getEntityTableData(destinations, connections, destinationDefinitions, "destination");

  const clickRow = (destination: EntityTableDataItem) => navigate(`${destination.entityId}`);

  return <ImplementationTable data={data} onClickRow={clickRow} entity="destination" />;
};

export default DestinationsTable;
