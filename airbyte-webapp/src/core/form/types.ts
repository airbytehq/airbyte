import { JSONSchema7Type, JSONSchema7TypeName } from "json-schema";

import { AirbyteJSONSchema } from "core/jsonSchema/types";

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
  properties: FormBlock[];
}

export interface FormConditionItem extends FormItem {
  _type: "formCondition";
  conditions: FormGroupItem[];
  /**
   * The full path to the const property describing which condition is selected (e.g. connectionConfiguration.a.deep.path.type)
   */
  selectionPath: string;
  /**
   * The key of the const property describing which condition is selected (e.g. type)
   */
  selectionKey: string;
  /**
   * The possible values of the selectionKey property ordered in the same way as the conditions
   */
  selectionConstValues: JSONSchema7Type[];
}

export interface FormObjectArrayItem extends FormItem {
  _type: "objectArray";
  properties: FormBlock;
}

export type FormBlock = FormGroupItem | FormBaseItem | FormConditionItem | FormObjectArrayItem;
