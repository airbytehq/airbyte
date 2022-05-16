import React from "react";

import { ImplementationTable } from "components/EntityTable";
import { EntityTableDataItem } from "components/EntityTable/types";
import { getEntityTableData } from "components/EntityTable/utils";

import { Destination } from "core/domain/connector";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

type IProps = {
  destinations: Destination[];
};

const DestinationsTable: React.FC<IProps> = ({ destinations }) => {
  const { push } = useRouter();
  const { connections } = useConnectionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getEntityTableData(destinations, connections, destinationDefinitions, "destination");

  const clickRow = (destination: EntityTableDataItem) => push(`${destination.entityId}`);

  return <ImplementationTable data={data} onClickRow={clickRow} entity="destination" />;
};

export default DestinationsTable;
