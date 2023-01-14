import { JSONSchema7TypeName } from "json-schema";

import { AirbyteJSONSchema } from "core/jsonSchema";

/**
 * When turning the JSON schema into `FormBlock`s,
 * some often used props are copied over for easy access.
 */
type FormRelevantJSONSchema = Pick<
  AirbyteJSONSchema,
  | "default"
  | "examples"
  | "description"
  | "pattern"
  | "order"
  | "const"
  | "title"
  | "airbyte_hidden"
  | "enum"
  | "format"
>;

interface FormItem extends FormRelevantJSONSchema {
  fieldKey: string;
  path: string;
  isRequired: boolean;
}

export interface FormBaseItem extends FormItem {
  _type: "formItem";
  type: JSONSchema7TypeName;
  isSecret?: boolean;
  multiline?: boolean;
}

export interface FormGroupItem extends FormItem {
  _type: "formGroup";
  jsonSchema: AirbyteJSONSchema;
  properties: FormBlock[];
}

export interface FormConditionItem extends FormItem {
  _type: "formCondition";
  conditions: Record<string, FormGroupItem | FormBaseItem>;
}

export interface FormObjectArrayItem extends FormItem {
  _type: "objectArray";
  properties: FormBlock;
}

export type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem | FormObjectArrayItem;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WidgetConfig = Record<string, any>;
export type WidgetConfigMap = Record<string, WidgetConfig>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type FormComponentOverrideProps = Record<string, any>;
