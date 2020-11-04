import { JSONSchema6, JSONSchema6Type, JSONSchema6TypeName } from "json-schema";

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema6TypeName;
  fieldKey: string;
  fieldName: string;
  isRequired: boolean;
  meta?: { [key: string]: any };
  title?: string;
  // description?: string;
  // default?: JSONSchema6Type;
  // examples?: JSONSchema6Type[] | undefined;
} & Partial<JSONSchema6>;

type FormGroupItem = {
  _type: "formGroup";
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  properties: FormBlock[];
  isLoading?: boolean;
  title?: string;
  description?: string;
  default?: JSONSchema6Type;
  examples?: JSONSchema6Type[] | undefined;
};

type FormConditionItem = {
  _type: "formCondition";
  title?: string;
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  conditions: { [key: string]: FormGroupItem | FormBaseItem };
  isLoading?: boolean;
};

export type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem;

export type WidgetConfig = { [key: string]: any };
export type WidgetConfigMap = { [key: string]: WidgetConfig };
