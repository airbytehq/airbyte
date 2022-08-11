import { useFormikContext, setIn } from "formik";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { Label, DropDown } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import GroupControls from "components/GroupControls";

import { FormBlock, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

import { useServiceForm } from "../../serviceFormContext";
import { ServiceFormValues } from "../../types";
import styles from "./ConditionSection.module.scss";
import { FormSection } from "./FormSection";

const GroupLabel = styled(Label)`
  width: auto;
  margin-right: 8px;
  padding-top: 8px;
  display: inline-block;
  padding-bottom: 0px;
  vertical-align: middle;
`;

const ConditionControls = styled.div`
  padding-top: 25px;
`;

interface ConditionSectionProps {
  formField: FormConditionItem;
  path?: string;
  disabled?: boolean;
}

/**
 * ConditionSection is responsible for handling oneOf sections of form
 */
export const ConditionSection: React.FC<ConditionSectionProps> = ({ formField, path, disabled }) => {
  const { widgetsInfo, setUiWidgetsInfo } = useServiceForm();
  const { values, setValues } = useFormikContext<ServiceFormValues>();

  const currentlySelectedCondition = widgetsInfo[formField.path]?.selectedItem;

  const onOptionChange = useCallback(
    (selectedItem: IDataItem) => {
      const newSelectedPath = formField.conditions[selectedItem.value];

      const newValues =
        newSelectedPath._type === "formGroup"
          ? newSelectedPath.properties?.reduce(
              (acc: ServiceFormValues, property: FormBlock) =>
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
  const label = formField.title || formField.fieldKey;

  return (
    <GroupControls
      key={`form-field-group-${formField.fieldKey}`}
      description={formField.description}
      fullWidthTitle
      title={
        <div className={styles.sectionTitle}>
          {label ? <GroupLabel>{label}:</GroupLabel> : null}
          <DropDown
            className={styles.sectionTitleDropdown}
            options={options}
            onChange={onOptionChange}
            value={currentlySelectedCondition}
            name={formField.path}
            isDisabled={disabled}
          />
        </div>
      }
    >
      <ConditionControls>
        <FormSection
          blocks={formField.conditions[currentlySelectedCondition]}
          path={path}
          disabled={disabled}
          skipAppend
        />
      </ConditionControls>
    </GroupControls>
  );
};
