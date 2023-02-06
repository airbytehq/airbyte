import { useFormikContext, setIn, useField } from "formik";
import clone from "lodash/clone";
import get from "lodash/get";
import React, { useCallback, useMemo } from "react";

import GroupControls from "components/GroupControls";
import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";

import { FormConditionItem } from "core/form/types";

import styles from "./ConditionSection.module.scss";
import { FormSection } from "./FormSection";
import { GroupLabel } from "./GroupLabel";
import { SectionContainer } from "./SectionContainer";
import { ConnectorFormValues } from "../../types";
import { setDefaultValues } from "../../useBuildForm";

interface ConditionSectionProps {
  formField: FormConditionItem;
  path: string;
  disabled?: boolean;
}

/**
 * ConditionSection is responsible for handling oneOf sections of form
 */
export const ConditionSection: React.FC<ConditionSectionProps> = ({ formField, path, disabled }) => {
  const { values, setValues } = useFormikContext<ConnectorFormValues>();

  const [, meta] = useField(path);

  // the value at selectionPath determines which condition is selected
  const currentSelectionValue = get(values, formField.selectionPath);
  let currentlySelectedCondition: number | undefined = formField.selectionConstValues.indexOf(currentSelectionValue);
  if (currentlySelectedCondition === -1) {
    // there should always be a matching condition, but in some edge cases
    // (e.g. breaking changes in specs) it's possible to have no matching value.
    currentlySelectedCondition = undefined;
  }

  const onOptionChange = useCallback(
    (selectedItem: DropDownOptionDataItem) => {
      const newSelectedFormBlock = formField.conditions[selectedItem.value];

      const conditionValues = clone(get(values, path) || {});
      conditionValues[formField.selectionKey] = formField.selectionConstValues[selectedItem.value];
      setDefaultValues(newSelectedFormBlock, conditionValues, { respectExistingValues: true });

      setValues(setIn(values, path, conditionValues));
    },
    [formField.conditions, formField.selectionKey, formField.selectionConstValues, values, path, setValues]
  );

  const options = useMemo(
    () =>
      formField.conditions.map((condition, index) => ({
        label: condition.title,
        value: index,
      })),
    [formField.conditions]
  );

  return (
    <SectionContainer>
      <GroupControls
        key={`form-field-group-${formField.fieldKey}`}
        label={<GroupLabel formField={formField} />}
        control={
          <DropDown
            options={options}
            onChange={onOptionChange}
            value={currentlySelectedCondition}
            name={formField.path}
            isDisabled={disabled}
            error={typeof meta.error === "string" && !!meta.error}
          />
        }
        controlClassName={styles.dropdown}
      >
        {/* currentlySelectedCondition is only falsy if a malformed config is loaded which doesn't have a valid value for the const selection key. In this case, render the selection group as empty. */}
        {typeof currentlySelectedCondition !== "undefined" && (
          <FormSection
            blocks={formField.conditions[currentlySelectedCondition]}
            path={path}
            disabled={disabled}
            skipAppend
          />
        )}
      </GroupControls>
    </SectionContainer>
  );
};
