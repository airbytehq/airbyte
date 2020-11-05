import { FormBlock, WidgetConfigMap } from "./types";
import at from "lodash.at";

export const buildPathInitialState = (
  formBlock: FormBlock[],
  formValues: { [key: string]: any },
  widgetState: WidgetConfigMap
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
        return widgetStateBuilder;
      case "formCondition":
        const defaultCondition = Object.entries(formItem.conditions).find(
          ([, subConditionItems]) => {
            switch (subConditionItems._type) {
              case "formGroup":
                return subConditionItems.properties.every(
                  p => at(formValues, p.fieldName) !== undefined
                );
              case "formItem":
                return at(formValues, subConditionItems.fieldName);
            }
            return false;
          }
        )?.[0];

        const selectedPath =
          defaultCondition ?? Object.keys(formItem.conditions)?.[0];
        widgetStateBuilder[formItem.fieldName] = {
          selectedItem: selectedPath
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
