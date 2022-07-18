import { useFormikContext, setIn } from "formik";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import styled from "styled-components";

import { Label, DropDown } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import GroupControls from "components/GroupControls";

import { FormBlock, FormConditionItem } from "core/form/types";
import { isDefined } from "utils/common";

import { useServiceForm } from "../../serviceFormContext";
import { ServiceFormValues } from "../../types";
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
  const { values, setValues, validateForm } = useFormikContext<ServiceFormValues>();
  const shouldValidateRef = useRef<boolean>(false);

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

      // Wait until the form state updates to run validation with the updated schema
      shouldValidateRef.current = true;

      setValues(newValues, false);
      setUiWidgetsInfo(formField.path, {
        selectedItem: selectedItem.value,
      });
    },
    [formField.conditions, formField.path, values, setValues, setUiWidgetsInfo]
  );

  const options = useMemo(
    () =>
      Object.keys(formField.conditions).map((dataItem) => ({
        label: dataItem,
        value: dataItem,
      })),
    [formField.conditions]
  );

  useEffect(() => {
    if (shouldValidateRef.current) {
      validateForm();
      shouldValidateRef.current = false;
    }
  }, [validateForm, widgetsInfo]);

  const label = formField.title || formField.fieldKey;
  const blocks = formField.conditions[currentlySelectedCondition];

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
            isDisabled={disabled}
          />
        </>
      }
    >
      <ConditionControls>
        <FormSection blocks={blocks} path={path} disabled={disabled} skipAppend />
      </ConditionControls>
    </GroupControls>
  );
};
