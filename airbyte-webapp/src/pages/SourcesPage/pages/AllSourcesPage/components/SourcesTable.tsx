import React from "react";

import { ImplementationTable } from "components/EntityTable";
import { EntityTableDataItem } from "components/EntityTable/types";
import { getEntityTableData } from "components/EntityTable/utils";

import { SourceRead } from "core/request/AirbyteClient";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { useSourceDefinitionList } from "../../../../../services/connector/SourceDefinitionService";

interface SourcesTableProps {
  sources: SourceRead[];
}

const SourcesTable: React.FC<SourcesTableProps> = ({ sources }) => {
  const { push } = useRouter();

  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const data = getEntityTableData(sources, connections, sourceDefinitions, "source");

  const clickRow = (source: EntityTableDataItem) => push(`${source.entityId}`);

  return <ImplementationTable data={data} onClickRow={clickRow} entity="source" />;
};

export default SourcesTable;
