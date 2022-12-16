import { JSONSchema7, JSONSchema7Type } from "json-schema";
import * as yup from "yup";

import { FormBlock, FormGroupItem, FormObjectArrayItem, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

import { FormBuildError } from "./FormBuildError";

/**
 * Returns yup.schema for validation
 *
 * This method builds yup schema based on jsonSchema ${@link JSONSchema7} and the derived ${@link FormBlock}.
 * Every property is walked through recursively in case it is condition | object | array.
 *
 * @param jsonSchema
 * @param formField The corresponding {@link FormBlock} to the given schema
 * @param parentSchema used in recursive schema building as required fields can be described in parentSchema
 * @param propertyKey used in recursive schema building for building path for uiConfig
 * @param propertyPath constructs path of property
 */
export const buildYupFormForJsonSchema = (
  jsonSchema: JSONSchema7,
  formField: FormBlock,
  parentSchema?: JSONSchema7,
  propertyKey?: string,
  propertyPath: string | undefined = propertyKey
): yup.AnySchema => {
  let schema:
    | yup.NumberSchema
    | yup.StringSchema
    | yup.AnyObjectSchema
    | yup.ArraySchema<yup.AnySchema>
    | yup.BooleanSchema
    | null = null;

  if (jsonSchema.oneOf && propertyPath) {
    const conditionFormField = formField as FormConditionItem;
    // for all keys in all of the possible objects from the oneOf, collect the sub yup-schema in a map.
    // the keys of the map are the keys of the property, the value is an array of the selection const value
    // for the condition plus the sub schema for that property in that condition.
    // As not all keys will show up in every condition, there can be a different number of possible sub schemas
    // per key; at least one and at max the number of conditions (if a key is part of every oneOf)
    // For example:
    // If there are three possible schemas with the following properties:
    //   A: { type: "A", prop1: number, prop2: string }
    //   B: { type: "B", prop1: string, prop2: string }
    //   C: { type: "C", prop2: boolean }
    // Then the map will look like this:
    //  {
    //    prop1: [["A", number], ["B", string]]
    //    prop2: [["A", string], ["B", string], ["C", boolean]]
    //  }
    const flattenedKeys: Map<string, Array<[JSONSchema7Type, yup.AnySchema]>> = new Map();
    jsonSchema.oneOf.forEach((condition, index) => {
      if (typeof condition !== "object") {
        throw new FormBuildError("connectorForm.error.oneOfWithNonObjects");
      }
      const selectionConstValue = conditionFormField.selectionConstValues[index];
      const selectionFormField = conditionFormField.conditions[index];
      Object.entries(condition.properties || {}).forEach(([key, prop], propertyIndex) => {
        if (!flattenedKeys.has(key)) {
          flattenedKeys.set(key, []);
        }
        flattenedKeys
          .get(key)
          ?.push([
            selectionConstValue,
            typeof prop === "boolean"
              ? yup.bool()
              : buildYupFormForJsonSchema(
                  prop,
                  selectionFormField.properties[propertyIndex],
                  condition,
                  key,
                  propertyPath ? `${propertyPath}.${propertyKey}` : propertyKey
                ),
          ]);
      });
    });
    const selectionKey = conditionFormField.selectionKey;

    // build the final object with all the keys - add "when" clauses to apply the
    // right sub-schema depending on which selection const value is defined.
    // if a key doesn't have a sub schema for a selection const value, set it to "strip"
    // so it's removed before the form is sent to the server
    // For example (the map from above):
    // {
    //   prop1: number.when(type == "A"), string.when(type == "B"), strip.when(type neither "A" nor "B")
    //   prop2: string.when(type == "A"), string.when(type == "B"), boolean.when(type == "C"), strip.when(type neither "A" nor "B" nor "C")
    // }
    return yup.object().shape(
      Object.fromEntries(
        Array.from(flattenedKeys.entries()).map(([key, schemaByCondition]) => {
          let mergedSchema = yup.mixed();
          if (key === selectionKey) {
            // do not validate the selectionKey itself, as the user can't change it it doesnt matter
            return [key, mergedSchema];
          }
          const allSelectionConstValuesWithThisKey = schemaByCondition.map(([constValue]) => constValue);
          schemaByCondition.forEach(([selectionConstValue, conditionalSchema]) => {
            mergedSchema = mergedSchema.when(selectionKey, {
              is: selectionConstValue,
              then: () => conditionalSchema,
              otherwise: (schema) => schema,
            });
          });
          mergedSchema = mergedSchema.when(selectionKey, {
            is: (val: JSONSchema7Type | undefined) =>
              // if typeof val is actually undefined, we are dealing with an inconsistent configuration which doesn't have any value for the condition key.
              // in this case, just keep the existing value to prevent data loss.
              typeof val !== "undefined" && !allSelectionConstValuesWithThisKey.includes(val),
            then: (schema) => schema.strip(),
            otherwise: (schema) => schema,
          });
          return [key, mergedSchema];
        })
      )
    );
  }

  switch (jsonSchema.type) {
    case "string":
      schema = yup
        .string()
        .transform((val) => String(val))
        .trim();

      if (jsonSchema?.pattern !== undefined) {
        schema = schema.matches(new RegExp(jsonSchema.pattern), "form.pattern.error");
      }

      break;
    case "boolean":
      schema = yup.boolean();
      break;
    case "integer":
    case "number":
      schema = yup.number().transform((value) => (isNaN(value) ? undefined : value));

      if (jsonSchema?.minimum !== undefined) {
        schema = schema.min(jsonSchema?.minimum);
      }

      if (jsonSchema?.maximum !== undefined) {
        schema = schema.max(jsonSchema?.maximum);
      }
      break;
    case "array":
      if (typeof jsonSchema.items === "object" && !Array.isArray(jsonSchema.items)) {
        schema = yup
          .array()
          .of(
            buildYupFormForJsonSchema(
              jsonSchema.items,
              (formField as FormObjectArrayItem).properties,
              jsonSchema,
              propertyKey,
              propertyPath ? `${propertyPath}.${propertyKey}` : propertyKey
            )
          );
      }
      break;
    case "object":
      let objectSchema = yup.object();

      const keyEntries = Object.entries(jsonSchema.properties || {}).map(([propertyKey, propertySchema]) => {
        const correspondingFormField = (formField as FormGroupItem).properties.find(
          (property) => property.fieldKey === propertyKey
        );
        if (!correspondingFormField) {
          throw new Error("mismatch between form fields and schema");
        }
        return [
          propertyKey,
          typeof propertySchema !== "boolean"
            ? buildYupFormForJsonSchema(
                propertySchema,
                correspondingFormField,
                jsonSchema,
                propertyKey,
                propertyPath ? `${propertyPath}.${propertyKey}` : propertyKey
              )
            : yup.bool(),
        ];
      });

      if (keyEntries.length) {
        objectSchema = objectSchema.shape(Object.fromEntries(keyEntries));
      } else {
        objectSchema = objectSchema.default({});
      }

      schema = objectSchema;
  }

  if (schema) {
    const hasDefault = isDefined(jsonSchema.default);

    if (hasDefault) {
      // @ts-expect-error can't infer correct type here so lets just use default from json_schema
      schema = schema.default(jsonSchema.default);
    }

    if (!hasDefault && jsonSchema.const) {
      // @ts-expect-error can't infer correct type here so lets just use default from json_schema
      schema = schema.oneOf([jsonSchema.const]).default(jsonSchema.const);
    }

    if (jsonSchema.enum) {
      // @ts-expect-error as enum is array we are going to use it as oneOf for yup
      schema = schema.oneOf(jsonSchema.enum);
    }

    const isRequired =
      !hasDefault &&
      parentSchema &&
      Array.isArray(parentSchema?.required) &&
      parentSchema.required.find((item) => item === propertyKey);

    if (schema && isRequired) {
      schema = schema.required("form.empty.error");
    }
  }

  return schema || yup.mixed();
};
