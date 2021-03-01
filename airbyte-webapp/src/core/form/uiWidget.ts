import get from "lodash.get";
import { FormBlock, WidgetConfigMap } from "./types";
import { buildYupFormForJsonSchema } from "../jsonSchema/schemaToYup";

export const buildPathInitialState = (
  formBlock: FormBlock[],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formValues: { [key: string]: any },
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
        widgetStateBuilder[formItem.fieldName] = {};
        return widgetStateBuilder;
      case "formCondition":
        const defaultCondition = Object.entries(formItem.conditions).find(
          ([key, subConditionItems]) => {
            switch (subConditionItems._type) {
              case "formGroup":
                const selectedValues = get(
                  formValues,
                  subConditionItems.fieldName
                );

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

        widgetStateBuilder[formItem.fieldName] = {
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
