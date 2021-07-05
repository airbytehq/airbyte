import { JSONSchema7, JSONSchema7Definition } from "json-schema";

interface AirbyteJSONSchemaProps extends JSONSchema7 {
  airbyte_secret?: boolean;
  multiline?: boolean;
  order?: number;
}

/**
 * Extends type y replacing all Types with ExtendedType
 */
type ExtendedRecursiveType<Type, ExtendedType extends Type> = {
  [Property in keyof ExtendedType]: ExtendedType[Property] extends Type
    ? ExtendedType
    : ExtendedType[Property] extends {
        [key: string]: Type;
      }
    ? {
        [key: string]: ExtendedRecursiveType<Type, ExtendedType>;
      }
    : ExtendedType[Property];
};

// /**
//  * Remaps all {@link JSONSchema7} to Airbyte Json schema
//  */
// export type AirbyteJSONSchemaTypeDefinition = ExtendedRecursiveType<
//   JSONSchema7Definition,
//   AirbyteJSONSchemaProps
// >;

/**
 * Remaps all {@link JSONSchema7} to Airbyte Json schema
 */
export type AirbyteJSONSchemaTypeDefinition = {
  [Property in keyof JSONSchema7]: JSONSchema7[Property] extends JSONSchema7Definition
    ? AirbyteJSONSchemaTypeDefinition
    : JSONSchema7[Property] extends boolean
    ? boolean
    : JSONSchema7[Property] extends {
        [key: string]: AirbyteJSONSchemaTypeDefinition;
      }
    ? AirbyteJSONSchemaTypeDefinition
    : JSONSchema7[Property];
} &
  AirbyteJSONSchemaProps;

export type AirbyteJSONSchema = AirbyteJSONSchemaTypeDefinition | boolean;
