import { JSONSchema7 } from "json-schema";

import { AirbyteCatalog, AirbyteStreamAndConfiguration } from "../../request/AirbyteClient";

export type SchemaFields = JSONSchema7;

export interface SyncSchemaStream extends AirbyteStreamAndConfiguration {
  /**
   * This field is not returned from API and is used to track unique objects
   */
  id?: string;
}

export interface SyncSchema extends AirbyteCatalog {
  streams: SyncSchemaStream[];
}

export type Path = string[];
