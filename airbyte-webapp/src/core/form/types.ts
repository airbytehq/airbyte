import { JSONSchema7, JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  fieldKey: string;
  fieldName: string;
  isRequired: boolean;
  isSecret?: boolean;
  title?: string;
  multiline?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  meta?: { [key: string]: any };
} & Partial<JSONSchema7>;

type FormGroupItem = {
  _type: "formGroup";
  fieldName: string;
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
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  title?: string;
  conditions: { [key: string]: FormGroupItem | FormBaseItem };
};

type FormObjectArrayItem = {
  _type: "objectArray";
  fieldName: string;
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
