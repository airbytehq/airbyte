import { JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

import { AirbyteJSONSchema } from "core/jsonSchema";

interface FormItem {
  fieldKey: string;
  path: string;
  isRequired: boolean;
  order?: number;
  title?: string;
  description?: string;
  airbyte_hidden?: boolean;
}

export interface FormBaseItem extends FormItem, AirbyteJSONSchema {
  _type: "formItem";
  type: JSONSchema7TypeName;
  isSecret?: boolean;
  multiline?: boolean;
  default?: JSONSchema7Type;
}

export interface FormGroupItem extends FormItem {
  _type: "formGroup";
  jsonSchema: AirbyteJSONSchema;
  properties: FormBlock[];
  isLoading?: boolean;
  hasOauth?: boolean;
  examples?: JSONSchema7Type;
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
