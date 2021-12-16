import get from "lodash/get";
import { buildYupFormForJsonSchema } from "core/jsonSchema/schemaToYup";
import { FormBlock, WidgetConfigMap } from "./types";
import { isDefined } from "utils/common";

export const buildPathInitialState = (
  formBlock: FormBlock[],
  formValues: { [key: string]: unknown },
  widgetState: WidgetConfigMap = {}
): { [key: string]: WidgetConfigMap } =>
  formBlock.reduce((widgetStateBuilder, formItem) => {
    switch (formItem._type) {
      case "formGroup":
        return buildPathInitialState(
          formItem.properties,
          formValues,
          widgetStateBuilder
        );
      case "formItem": {
        const resultObject: Record<string, unknown> = {};

        if (isDefined(formItem.const)) {
          resultObject.const = formItem.const;
        }

        widgetStateBuilder[formItem.path] = resultObject;
        return widgetStateBuilder;
      }
      case "formCondition": {
        const defaultCondition = Object.entries(formItem.conditions).find(
          ([key, subConditionItems]) => {
            switch (subConditionItems._type) {
              case "formGroup": {
                const selectedValues = get(formValues, subConditionItems.path);

                const subPathSchema = buildYupFormForJsonSchema({
                  type: "object",
                  ...subConditionItems.jsonSchema,
                });

                if (subPathSchema.isValidSync(selectedValues)) {
                  return key;
                }
                return null;
              }
              case "formItem":
                return key;
            }

            return null;
          }
        )?.[0];

        const selectedPath =
          defaultCondition ?? Object.keys(formItem.conditions)?.[0];

        widgetStateBuilder[formItem.path] = {
          selectedItem: selectedPath,
        };

        if (formItem.conditions[selectedPath]) {
          return buildPathInitialState(
            [formItem.conditions[selectedPath]],
            formValues,
            widgetStateBuilder
          );
        }
      }
    }

    return widgetStateBuilder;
  }, widgetState);
