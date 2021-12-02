import React, { useCallback, useMemo } from "react";
import styled from "styled-components";
import { useFormikContext, setIn } from "formik";

import { Label, DropDown } from "components";

import { useServiceForm } from "../../serviceFormContext";
import { ServiceFormValues } from "../../types";

import { FormBlock, FormConditionItem } from "core/form/types";
import { IDataItem } from "components/base/DropDown/components/Option";
import GroupControls from "components/GroupControls";
import { FormSection } from "./FormSection";
import { isDefined } from "utils/common";

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
