import React from "react";

import { ImplementationTable } from "components/EntityTable";
import { EntityTableDataItem } from "components/EntityTable/types";
import { getEntityTableData } from "components/EntityTable/utils";

import { Source } from "core/domain/connector";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { useSourceDefinitionList } from "../../../../../services/connector/SourceDefinitionService";

type IProps = {
  sources: Source[];
};

const SourcesTable: React.FC<IProps> = ({ sources }) => {
  const { push } = useRouter();

  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const data = getEntityTableData(sources, connections, sourceDefinitions, "source");

  const clickRow = (source: EntityTableDataItem) => push(`${source.entityId}`);

  return <ImplementationTable data={data} onClickRow={clickRow} entity="source" />;
};

export default SourcesTable;
