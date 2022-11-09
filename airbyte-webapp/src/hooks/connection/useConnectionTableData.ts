import { ITableDataItem } from "components/EntityTable/types";
import { ConnectionTableDataType, getConnectionTableData } from "components/EntityTable/utils";

import { WebBackendConnectionListItem } from "core/request/AirbyteClient";

export const useConnectionsTableData = (
  connections: WebBackendConnectionListItem[],
  type: ConnectionTableDataType
): ITableDataItem[] => {
  const isSchemaChangesFeatureEnabled = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES === "true";

  return getConnectionTableData({ connections, type, isSchemaChangesFeatureEnabled });
};
