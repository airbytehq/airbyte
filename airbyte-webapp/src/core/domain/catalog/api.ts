import { JSONSchema7 } from "json-schema";
import { JobInfo } from "../job/Job";

export interface SourceDiscoverSchemaRead {
  catalog: SyncSchema;
  jobInfo?: JobInfo;
}

export type SchemaFields = JSONSchema7;

export enum SyncMode {
  Incremental = "incremental",
  FullRefresh = "full_refresh",
}

export enum DestinationSyncMode {
  Overwrite = "overwrite",
  Append = "append",
  Dedupted = "append_dedup",
}

export type SyncSchemaStreamInner = {
  stream: AirbyteStream;
  config: AirbyteStreamConfiguration;
};

export type SyncSchemaStream = {
  stream: AirbyteStream;
  config: AirbyteStreamConfiguration;

  id: string;
};

export type AirbyteStream = {
  name: string;
  namespace?: string;
  jsonSchema: SchemaFields;
  supportedSyncModes: SyncMode[];
  sourceDefinedCursor: boolean | null;
  sourceDefinedPrimaryKey: string[][];
  defaultCursorField: string[];
};

export type AirbyteStreamConfiguration = {
  cursorField: string[];
  primaryKey: string[][];
  selected: boolean;
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
  aliasName: string;
};

export type SyncSchema = {
  streams: SyncSchemaStream[];
};
