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
  selectedDestinationId: string;
  configSchema: JsonSchema;
}

export interface DestinationConfig {
  id: string;
  displayName: string;
  schema?: JsonSchema;
}

export interface StatusCodeResponse {
  schema?: JsonSchema;
  description?: string;
}

export interface EndpointData {
  configurationSchema?: JsonSchema;
  requestBodyProperties?: RequestBodyProperty[];
  responseBodyProperties?: ResponseBodyProperty[];
  responsesByStatus?: Record<string, StatusCodeResponse>;
  [key: string]: unknown;
}

export type OptionalEndpointData = EndpointData | null | undefined;

export interface RequestBodyProperty {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
}

export interface ResponseBodyProperty {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  readOnly?: boolean;
}

export type ApiEndpointsData = Record<string, EndpointData>;
