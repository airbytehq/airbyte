import { JSONSchema7, JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  fieldKey: string;
  fieldName: string;
  isRequired: boolean;
  meta?: { [key: string]: any };
  title?: string;
} & Partial<JSONSchema7>;

type FormGroupItem = {
  _type: "formGroup";
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  properties: FormBlock[];
  isLoading?: boolean;
  title?: string;
  description?: string;
  default?: JSONSchema7Type;
  examples?: JSONSchema7Type;
};

type FormConditionItem = {
  _type: "formCondition";
  title?: string;
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  conditions: { [key: string]: FormGroupItem | FormBaseItem };
};

export type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem;

export type WidgetConfig = { [key: string]: any };
export type WidgetConfigMap = { [key: string]: WidgetConfig };
