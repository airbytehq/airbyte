import React from "react";
import { useNavigate } from "react-router-dom";

import { ImplementationTable } from "components/EntityTable";
import { EntityTableDataItem } from "components/EntityTable/types";
import { getEntityTableData } from "components/EntityTable/utils";

import { SourceRead } from "core/request/AirbyteClient";
import { useConnectionList } from "hooks/services/useConnectionHook";

import { useSourceDefinitionList } from "../../../../../services/connector/SourceDefinitionService";

interface SourcesTableProps {
  sources: SourceRead[];
}

const SourcesTable: React.FC<SourcesTableProps> = ({ sources }) => {
  const navigate = useNavigate();

  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const data = getEntityTableData(sources, connections, sourceDefinitions, "source");

  const clickRow = (source: EntityTableDataItem) => navigate(`${source.entityId}`);

  return <ImplementationTable data={data} onClickRow={clickRow} entity="source" />;
};

export default SourcesTable;
