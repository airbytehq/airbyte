import { JSONSchema7 } from "json-schema";

import { AirbyteStreamAndConfiguration } from "../../request/AirbyteClient";
import { JobInfo } from "../job";

export interface SourceDiscoverSchemaRead {
  catalog: SyncSchema;
  jobInfo?: JobInfo;
  catalogId: string;
}

export type SchemaFields = JSONSchema7;

export enum SyncMode {
  Incremental = "incremental",
  FullRefresh = "full_refresh",
}

export enum DestinationSyncMode {
  Overwrite = "overwrite",
  Append = "append",
  Deduped = "append_dedup",
}

export type SyncSchemaStreamInner = AirbyteStreamAndConfiguration;

export type SyncSchemaStream = SyncSchemaStreamInner & {
  /**
   * This field is not returned from API and is used to track unique objects
   */
  id: string;
};

export type AirbyteStream = {
  name: string;
  namespace?: string;
  jsonSchema: SchemaFields;
  supportedSyncModes: SyncMode[];
  sourceDefinedCursor: boolean | null;
  sourceDefinedPrimaryKey: Path[];
  defaultCursorField: Path;
};

export type AirbyteStreamConfiguration = {
  cursorField: Path;
  primaryKey: Path[];
  selected: boolean;
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
  aliasName: string;
};

export type SyncSchema = {
  streams: AirbyteStreamAndConfiguration[];
};

export type Path = string[];
