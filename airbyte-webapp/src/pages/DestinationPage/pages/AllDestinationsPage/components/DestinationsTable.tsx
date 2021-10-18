import React from "react";

import { ImplementationTable } from "components/EntityTable";
import { getEntityTableData } from "components/EntityTable/utils";
import { EntityTableDataItem } from "components/EntityTable/types";

import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import { Destination } from "core/resources/Destination";
import { useDestinationDefinitionList } from "hooks/services/useDestinationDefinition";
import { useConnectionList } from "hooks/services/useConnectionHook";

type IProps = {
  destinations: Destination[];
};

const DestinationsTable: React.FC<IProps> = ({ destinations }) => {
  const { push } = useRouter();
  const { connections } = useConnectionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const data = getEntityTableData(
    destinations,
    connections,
    destinationDefinitions,
    "destination"
  );

  const clickRow = (destination: EntityTableDataItem) =>
    push(`${Routes.Destination}/${destination.entityId}`);

  return (
    <ImplementationTable
      data={data}
      onClickRow={clickRow}
      entity="destination"
    />
  );
};

export default DestinationsTable;
