export interface JsonSchema {
  type?: string;
  title?: string;
  description?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  oneOf?: JsonSchema[];
  [key: string]: unknown;
}

export interface ConfigSchemaProps {
  selectedSourceId: string;
  configSchema: JsonSchema;
}

export interface SourceConfig {
  id: string;
  displayName: string;
  schema?: JsonSchema;
}

export interface EndpointData {
  configurationSchema?: JsonSchema;
  requestBodyProperties?: RequestBodyProperty[];
  [key: string]: unknown;
}

export type OptionalEndpointData = EndpointData | null | undefined;

export interface RequestBodyProperty {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
}

export type ApiEndpointsData = Record<string, EndpointData>;
