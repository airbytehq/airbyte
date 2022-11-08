import { useFormikContext, setIn } from "formik";
import React, { useCallback, useMemo } from "react";

import GroupControls from "components/GroupControls";
import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";

import { FormBlock, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

import { useConnectorForm } from "../../connectorFormContext";
import { ConnectorFormValues } from "../../types";
import styles from "./ConditionSection.module.scss";
import { FormSection } from "./FormSection";
import { GroupLabel } from "./GroupLabel";

interface ConditionSectionProps {
  formField: FormConditionItem;
  path?: string;
  disabled?: boolean;
}

/**
 * ConditionSection is responsible for handling oneOf sections of form
 */
export const ConditionSection: React.FC<ConditionSectionProps> = ({ formField, path, disabled }) => {
  const { widgetsInfo, setUiWidgetsInfo } = useConnectorForm();
  const { values, setValues } = useFormikContext<ConnectorFormValues>();

  const currentlySelectedCondition = widgetsInfo[formField.path]?.selectedItem;

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
    <GroupControls
      key={`form-field-group-${formField.fieldKey}`}
      title={
        <>
          <GroupLabel formField={formField} />
          <DropDown
            className={styles.groupDropdown}
            options={options}
            onChange={onOptionChange}
            value={currentlySelectedCondition}
            name={formField.path}
            isDisabled={disabled}
          />
        </>
      }
    >
      <FormSection
        blocks={formField.conditions[currentlySelectedCondition]}
        path={path}
        disabled={disabled}
        skipAppend
      />
    </GroupControls>
  );
};
