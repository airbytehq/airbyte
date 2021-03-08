import { ScheduleProperties } from "core/resources/Connection";

type EntityTableDataItem = {
  entityId: string;
  entityName: string;
  connectorName: string;
  connectEntities: {
    name: string;
    connector: string;
    status: string;
  }[];
  enabled: boolean;
  lastSync?: number | null;
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
};

enum Status {
  ACTIVE = "active",
  INACTIVE = "inactive",
}

export type { ITableDataItem, EntityTableDataItem };
export { Status };
