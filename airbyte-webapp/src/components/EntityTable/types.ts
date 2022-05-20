import { ScheduleProperties } from "core/domain/connection";

type EntityTableDataItem = {
  entityId: string;
  entityName: string;
  connectorName: string;
  connectEntities: {
    name: string;
    connector: string;
    status: string;
    lastSyncStatus: string | null;
  }[];
  enabled: boolean;
  lastSync?: number | null;
  connectorIcon?: string;
};

type ITableDataItem = {
  connectionId: string;
  entityName: string;
  connectorName: string;
  enabled: boolean;
  isSyncing?: boolean;
  status?: string;
  lastSync?: number | null;
  schedule: ScheduleProperties | null;
  lastSyncStatus: string | null;
  connectorIcon?: string;
  entityIcon?: string;
};

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

export type { ITableDataItem, EntityTableDataItem };
export { Status, SortOrderEnum };
