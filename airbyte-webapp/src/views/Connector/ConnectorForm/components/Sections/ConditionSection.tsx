import { useFormikContext, setIn, useField } from "formik";
import get from "lodash/get";
import React, { useCallback, useMemo } from "react";

import GroupControls from "components/GroupControls";
import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";

import { FormBlock, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

import { useConnectorForm } from "../../connectorFormContext";
import { ConnectorFormValues } from "../../types";
import { FormSection } from "./FormSection";
import { GroupLabel } from "./GroupLabel";
import { SectionContainer } from "./SectionContainer";

interface ConditionSectionProps {
  formField: FormConditionItem;
  path: string;
  disabled?: boolean;
}

/**
 * ConditionSection is responsible for handling oneOf sections of form
 */
export const ConditionSection: React.FC<ConditionSectionProps> = ({ formField, path, disabled }) => {
  const { widgetsInfo, setUiWidgetsInfo } = useConnectorForm();
  const { values, setValues } = useFormikContext<ConnectorFormValues>();

  const [, meta] = useField(path);

  // the value at selectionPath determines which condition is selected
  const currentSelectionValue = get(values, formField.selectionPath);
  // in order to find the right condition key, we need to check for which condition
  // the "const" value matches the current value at selectionPath
  const currentlySelectedCondition = useMemo(() => {
    const possibleConditions = Object.entries(formField.conditions);
    const matchingCondition = possibleConditions.find(([, condition]) => {
      if (condition._type !== "formGroup") {
        return false;
      }
      return (
        condition.properties.find((property) => property.path === formField.selectionPath)?.const ===
        currentSelectionValue
      );
    });
    // there should always be a matching condition, but in some edge cases
    // (e.g. breaking changes in specs) it's possible to have no matching value.
    // In this case, default to the first condition
    return (matchingCondition || possibleConditions[0])[0];
  }, [currentSelectionValue, formField.conditions, formField.selectionPath]);

  const onOptionChange = useCallback(
    (selectedItem: DropDownOptionDataItem) => {
      const newSelectedPath = formField.conditions[selectedItem.value];

      const newValues =
        newSelectedPath._type === "formGroup"
          ? newSelectedPath.properties?.reduce(
              (acc: ConnectorFormValues, property: FormBlock) =>
                property._type === "formItem" && isDefined(property.const)
                  ? setIn(acc, property.path, property.const)
                  : acc,
              values
            )
          : values;

      setUiWidgetsInfo(formField.path, {
        selectedItem: selectedItem.value,
      });
      setValues(newValues);
    },
    [values, formField.conditions, setValues, setUiWidgetsInfo, formField.path]
  );

  const options = useMemo(
    () =>
      Object.keys(formField.conditions).map((dataItem) => ({
        label: dataItem,
        value: dataItem,
      })),
    [formField.conditions]
  );

  return (
    <SectionContainer>
      <GroupControls
        key={`form-field-group-${formField.fieldKey}`}
        label={<GroupLabel formField={formField} />}
        dropdown={
          <DropDown
            options={options}
            onChange={onOptionChange}
            value={currentlySelectedCondition}
            name={formField.path}
            isDisabled={disabled}
            error={typeof meta.error === "string" && !!meta.error}
          />
        }
      >
        <FormSection
          blocks={formField.conditions[currentlySelectedCondition]}
          path={path}
          disabled={disabled}
          skipAppend
        />
      </GroupControls>
    </SectionContainer>
  );
};
