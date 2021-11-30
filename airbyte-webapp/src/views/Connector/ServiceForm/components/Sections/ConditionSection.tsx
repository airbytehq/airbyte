import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { Label, DropDown } from "components";

import { FormConditionItem } from "core/form/types";
import { useServiceForm } from "../../serviceFormContext";
import { IDataItem } from "components/base/DropDown/components/Option";
import GroupControls from "components/GroupControls";
import { FormSection } from "./FormSection";
import { useFormikContext, setIn } from "formik";

const GroupLabel = styled(Label)`
  width: auto;
  margin-right: 8px;
  display: inline-block;
`;

const ConditionControls = styled.div`
  padding-top: 25px;
`;

/**
 * ConditionSection is responsible for handling oneOf sections of form
 */
export const ConditionSection: React.FC<{
  formField: FormConditionItem;
  path?: string;
}> = ({ formField, path }) => {
  const { widgetsInfo, setUiWidgetsInfo } = useServiceForm();
  const { values, setValues } = useFormikContext();

  const currentlySelectedCondition = widgetsInfo[formField.path]?.selectedItem;

  const options = useMemo(
    () =>
      Object.keys(formField.conditions).map((dataItem) => ({
        label: dataItem,
        value: dataItem,
      })),
    [formField.conditions]
  );
  const onOptionChange = useCallback(
    (selectedItem: IDataItem) => {
      setUiWidgetsInfo(formField.path, {
        selectedItem: selectedItem.value,
      });

      const newValues =
        // @ts-ignore
        formField.conditions[selectedItem.value].properties?.reduce(
          (acc: any, property: any) => {
            return property.const
              ? setIn(acc, property.path, property.const)
              : acc;
          },
          values
        ) ?? values;

      console.log(newValues);

      setValues(newValues);
    },
    [values, setUiWidgetsInfo, formField.path]
  );

  const label = formField.title || formField.fieldKey;

  return (
    <GroupControls
      key={`form-field-group-${formField.fieldKey}`}
      description={formField.description}
      title={
        <>
          {label ? <GroupLabel>{label}:</GroupLabel> : null}
          <DropDown
            options={options}
            onChange={onOptionChange}
            value={currentlySelectedCondition}
            name={formField.path}
          />
        </>
      }
    >
      <ConditionControls>
        <FormSection
          blocks={formField.conditions[currentlySelectedCondition]}
          path={path}
          skipAppend
        />
      </ConditionControls>
    </GroupControls>
  );
};
