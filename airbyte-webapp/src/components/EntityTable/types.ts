import { ConnectionScheduleDataBasicSchedule } from "../../core/request/AirbyteClient";

interface EntityTableDataItem {
  entityId: string;
  entityName: string;
  connectorName: string;
  connectEntities: Array<{
    name: string;
    connector: string;
    status: string;
    lastSyncStatus: string | null;
  }>;
  enabled: boolean;
  lastSync?: number | null;
  connectorIcon?: string;
}
interface SourceTableDataItem {
  sourceId: string;
  name: string;
  sourceName: string;
  sourceDefinitionId: string;
  workspaceId: string;
  connectionConfiguration: any;
}
interface ITableDataItem {
  connectionId: string;
  name: string;
  entityName: string;
  connectorName: string;
  enabled: boolean;
  isSyncing?: boolean;
  status?: string;
  lastSync?: number | null;
  schedule?: ConnectionScheduleDataBasicSchedule;
  lastSyncStatus: string | null;
  connectorIcon?: string;
  entityIcon?: string;
  latestSyncJobStatus?: string;
}

enum Status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  FAILED = "failed",
  EMPTY = "empty",
  PENDING = "pending",
}

enum SortOrderEnum {
  DESC = "desc",
  ASC = "asc",
}

export type { ITableDataItem, EntityTableDataItem, SourceTableDataItem };
export { Status, SortOrderEnum };
