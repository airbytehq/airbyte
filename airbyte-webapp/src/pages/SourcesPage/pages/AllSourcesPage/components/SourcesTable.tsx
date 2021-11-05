import React from "react";
import { useResource } from "rest-hooks";

import { ImplementationTable } from "components/EntityTable";
import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import { Source } from "core/resources/Source";
import ConnectionResource from "core/resources/Connection";
import { getEntityTableData } from "components/EntityTable/utils";
import { EntityTableDataItem } from "components/EntityTable/types";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  sources: Source[];
};

const SourcesTable: React.FC<IProps> = ({ sources }) => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const data = getEntityTableData(
    sources,
    connections,
    sourceDefinitions,
    "source"
  );

  const clickRow = (source: EntityTableDataItem) =>
    push(`${Routes.Source}/${source.entityId}`);

  return (
    <ImplementationTable data={data} onClickRow={clickRow} entity="source" />
  );
};

export default SourcesTable;
