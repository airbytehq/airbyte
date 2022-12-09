import { JSONSchema7, JSONSchema7Definition } from "json-schema";

interface AirbyteJSONSchemaProps {
  airbyte_secret?: boolean;
  airbyte_hidden?: boolean;
  multiline?: boolean;
  order?: number;
}

/**
 * Remaps all {@link JSONSchema7} to Airbyte Json schema
 */
export type AirbyteJSONSchema = {
  [Property in keyof JSONSchema7]+?: JSONSchema7[Property] extends boolean
    ? boolean
    : Property extends "properties" | "patternProperties" | "definitions"
    ? Record<string, AirbyteJSONSchemaDefinition>
    : JSONSchema7[Property] extends JSONSchema7Definition
    ? AirbyteJSONSchemaDefinition
    : JSONSchema7[Property] extends JSONSchema7Definition[]
    ? AirbyteJSONSchemaDefinition[]
    : JSONSchema7[Property] extends JSONSchema7Definition | JSONSchema7Definition[]
    ? AirbyteJSONSchemaDefinition | AirbyteJSONSchemaDefinition[]
    : JSONSchema7[Property];
} & AirbyteJSONSchemaProps;

export type AirbyteJSONSchemaDefinition = AirbyteJSONSchema | boolean;
