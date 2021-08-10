import { JSONSchema7, JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

type FormItem = {
  fieldKey: string;
  path: string;
  isRequired: boolean;
  order?: number;
  title?: string;
  description?: string;
};

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  isSecret?: boolean;
  multiline?: boolean;
} & FormItem &
  Partial<JSONSchema7>;

type FormGroupItem = {
  _type: "formGroup";
  jsonSchema: JSONSchema7;
  properties: FormBlock[];
  isLoading?: boolean;
  default?: JSONSchema7Type;
  examples?: JSONSchema7Type;
} & FormItem;

type FormConditionItem = {
  _type: "formCondition";
  conditions: { [key: string]: FormGroupItem | FormBaseItem };
} & FormItem;

type FormObjectArrayItem = {
  _type: "objectArray";
  properties: FormBlock;
} & FormItem;

type FormBlock =
  | FormGroupItem
  | FormBaseItem
  | FormConditionItem
  | FormObjectArrayItem;

export type {
  FormBlock,
  FormConditionItem,
  FormGroupItem,
  FormObjectArrayItem,
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WidgetConfig = { [key: string]: any };
export type WidgetConfigMap = { [key: string]: WidgetConfig };
