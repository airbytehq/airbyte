import React from "react";

import { ImplementationTable } from "components/EntityTable";
import { getEntityTableData } from "components/EntityTable/utils";
import { EntityTableDataItem } from "components/EntityTable/types";

import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import { Source } from "core/resources/Source";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceDefinitionList } from "hooks/services/useSourceDefinition";

type IProps = {
  sources: Source[];
};

const SourcesTable: React.FC<IProps> = ({ sources }) => {
  const { push } = useRouter();

  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();

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
