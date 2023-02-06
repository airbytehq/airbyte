import { ConnectionScheduleData, ConnectionScheduleType, SchemaChange } from "../../core/request/AirbyteClient";

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

interface ConnectionTableDataItem {
  connectionId: string;
  name: string;
  entityName: string;
  connectorName: string;
  enabled: boolean;
  isSyncing?: boolean;
  status?: string;
  lastSync?: number | null;
  scheduleData?: ConnectionScheduleData;
  scheduleType?: ConnectionScheduleType;
  schemaChange: SchemaChange;
  lastSyncStatus: string | null;
  connectorIcon?: string;
  entityIcon?: string;
}

const enum Status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  FAILED = "failed",
  CANCELLED = "cancelled",
  EMPTY = "empty",
  PENDING = "pending",
}

enum SortOrderEnum {
  DESC = "desc",
  ASC = "asc",
}

export type { ConnectionTableDataItem, EntityTableDataItem };
export { Status, SortOrderEnum };
