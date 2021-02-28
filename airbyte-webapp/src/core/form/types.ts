import { JSONSchema7, JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

export type FormBaseItem = {
  _type: "formItem";
  type: JSONSchema7TypeName;
  fieldKey: string;
  fieldName: string;
  isRequired: boolean;
  isSecret?: boolean;
  title?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  meta?: { [key: string]: any };
} & Partial<JSONSchema7>;

type FormGroupItem = {
  _type: "formGroup";
  fieldName: string;
  fieldKey: string;
  isRequired: boolean;
  title?: string;
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

export type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WidgetConfig = { [key: string]: any };
export type WidgetConfigMap = { [key: string]: WidgetConfig };
