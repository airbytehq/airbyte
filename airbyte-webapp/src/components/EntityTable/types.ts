import { ScheduleProperties } from "core/resources/Connection";

type EntityTableDataItem = {
  entityId: string;
  entityName: string;
  connectorName: string;
  connectEntities: {
    name: string;
    connector: string;
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
  lastSync?: number | null;
  schedule: ScheduleProperties | null;
};

export type { ITableDataItem, EntityTableDataItem };
