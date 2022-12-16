import { useFormikContext, setIn, useField } from "formik";
import get from "lodash/get";
import React, { useCallback, useMemo } from "react";

import GroupControls from "components/GroupControls";
import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";

import { FormBlock, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

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

      setValues(newValues);
    },
    [values, formField.conditions, setValues]
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
