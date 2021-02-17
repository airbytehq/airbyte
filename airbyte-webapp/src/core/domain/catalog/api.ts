import { JSONSchema7 } from "json-schema";
import { JobInfo } from "core/resources/Scheduler";

export interface SourceDiscoverSchemaRead {
  catalog: SyncSchema;
  jobInfo?: JobInfo;
}

export type SchemaFields = JSONSchema7;

export enum SyncMode {
  Incremental = "incremental",
  FullRefresh = "full_refresh"
}

export type SyncSchemaStream = {
  stream: AirbyteStream;
  config: AirbyteStreamConfiguration;
};

export type AirbyteStream = {
  name: string;
  jsonSchema: SchemaFields;
  supportedSyncModes: SyncMode[];
  sourceDefinedCursor: boolean | null;
  defaultCursorField: string[];
};

export type AirbyteStreamConfiguration = {
  cursorField: string[];
  selected: boolean;
  syncMode: string | null;
  aliasName: string;
};

export type SyncSchema = {
  streams: SyncSchemaStream[];
};
