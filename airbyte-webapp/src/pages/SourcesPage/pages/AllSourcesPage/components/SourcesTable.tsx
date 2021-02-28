import React from "react";
import { useResource } from "rest-hooks";

import { ImplementationTable } from "components/EntityTable";
import { Routes } from "pages/routes";
import useRouter from "components/hooks/useRouterHook";
import { Source } from "core/resources/Source";
import ConnectionResource from "core/resources/Connection";
import config from "config";
import { getEntityTableData } from "components/EntityTable/utils";
import { EntityTableDataItem } from "components/EntityTable/types";

type IProps = {
  sources: Source[];
};

const SourcesTable: React.FC<IProps> = ({ sources }) => {
  const { push } = useRouter();

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const data = getEntityTableData(sources, connections, "source");

  const clickRow = (source: EntityTableDataItem) =>
    push(`${Routes.Source}/${source.entityId}`);

  return (
    <ImplementationTable data={data} onClickRow={clickRow} entity="source" />
  );
};

export default SourcesTable;
