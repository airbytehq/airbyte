import get from "lodash.get";
import { FormBlock, WidgetConfigMap } from "./types";
import { buildYupFormForJsonSchema } from "core/jsonSchema/schemaToYup";

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
      case "formItem":
        widgetStateBuilder[formItem.path] = {};
        return widgetStateBuilder;
      case "formCondition":
        const defaultCondition = Object.entries(formItem.conditions).find(
          ([key, subConditionItems]) => {
            switch (subConditionItems._type) {
              case "formGroup":
                const selectedValues = get(formValues, subConditionItems.path);

                const subPathSchema = buildYupFormForJsonSchema({
                  type: "object",
                  ...subConditionItems.jsonSchema,
                });

                if (subPathSchema.isValidSync(selectedValues)) {
                  return key;
                }
                return null;
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

    return widgetStateBuilder;
  }, widgetState);
