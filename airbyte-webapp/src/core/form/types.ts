import { JSONSchema7, JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  fieldKey: string;
  path: string;
  isRequired: boolean;
  isSecret?: boolean;
  title?: string;
  multiline?: boolean;
} & Partial<JSONSchema7>;

type FormGroupItem = {
  _type: "formGroup";
  path: string;
  fieldKey: string;
  isRequired: boolean;
  title?: string;
  jsonSchema: JSONSchema7;
  properties: FormBlock[];
  isLoading?: boolean;
  description?: string;
  default?: JSONSchema7Type;
  examples?: JSONSchema7Type;
};

type FormConditionItem = {
  _type: "formCondition";
  path: string;
  fieldKey: string;
  isRequired: boolean;
  title?: string;
  conditions: { [key: string]: FormGroupItem | FormBaseItem };
};

type FormObjectArrayItem = {
  _type: "objectArray";
  path: string;
  fieldKey: string;
  isRequired: boolean;
  title?: string;
  properties: FormBlock;
};

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
