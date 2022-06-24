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

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  isSecret?: boolean;
  multiline?: boolean;
} & FormItem &
  AirbyteJSONSchema;

type FormGroupItem = {
  _type: "formGroup";
  jsonSchema: AirbyteJSONSchema;
  properties: FormBlock[];
  isLoading?: boolean;
  hasOauth?: boolean;
  default?: JSONSchema7Type;
  examples?: JSONSchema7Type;
} & FormItem;

type FormConditionItem = {
  _type: "formCondition";
  conditions: Record<string, FormGroupItem | FormBaseItem>;
} & FormItem;

type FormObjectArrayItem = {
  _type: "objectArray";
  properties: FormBlock;
} & FormItem;

type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem | FormObjectArrayItem;

export type { FormBlock, FormConditionItem, FormGroupItem, FormObjectArrayItem };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WidgetConfig = Record<string, any>;
export type WidgetConfigMap = Record<string, WidgetConfig>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type FormComponentOverrideProps = Record<string, any>;
