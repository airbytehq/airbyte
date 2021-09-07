import React from "react";
import { useResource } from "rest-hooks";

import { ImplementationTable } from "components/EntityTable";
import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import ConnectionResource from "core/resources/Connection";
import { Destination } from "core/resources/Destination";
import { getEntityTableData } from "components/EntityTable/utils";
import { EntityTableDataItem } from "components/EntityTable/types";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  destinations: Destination[];
};

const DestinationsTable: React.FC<IProps> = ({ destinations }) => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

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
