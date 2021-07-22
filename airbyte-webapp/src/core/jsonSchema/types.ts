import { JSONSchema7, JSONSchema7Definition } from "json-schema";

interface AirbyteJSONSchemaProps extends JSONSchema7 {
  airbyte_secret?: boolean;
  multiline?: boolean;
  order?: number;
}

type JsonSchemaRequired = Required<JSONSchema7>;

/**
 * Remaps all {@link JSONSchema7} to Airbyte Json schema
 */
export type AirbyteJSONSchemaTypeDefinition = {
  [Property in keyof JsonSchemaRequired]+?: JsonSchemaRequired[Property] extends JSONSchema7Definition
    ? AirbyteJSONSchemaTypeDefinition
    : JsonSchemaRequired[Property] extends boolean
    ? boolean
    : JsonSchemaRequired[Property] extends Array<JSONSchema7Definition>
    ? AirbyteJSONSchemaTypeDefinition[]
    : Property extends "properties"
    ? {
        [key: string]: AirbyteJSONSchemaTypeDefinition;
      }
    : JsonSchemaRequired[Property] extends
        | JSONSchema7Definition
        | JSONSchema7Definition[]
    ? AirbyteJSONSchemaTypeDefinition | AirbyteJSONSchemaTypeDefinition[]
    : JsonSchemaRequired[Property];
} &
  AirbyteJSONSchemaProps;

export type AirbyteJSONSchema = AirbyteJSONSchemaTypeDefinition | boolean;
