import React from "react";
import styled from "styled-components";

import { DropDown, Label } from "components";
import { FormBlock, FormConditionItem } from "core/form/types";
import { Property } from "./Property";
import { useServiceForm } from "../serviceFormContext";

const ItemSection = styled.div`
  margin-bottom: 27px;
`;

const FormItemGroupDropDown = styled(ItemSection)`
  margin-top: -17px;
  background: ${({ theme }) => theme.whiteColor};
  padding: 0 5px;
  display: inline-block;
  vertical-align: middle;

  & > div {
    min-width: 180px;
    display: inline-block;
  }
`;

const FormItemGroup = styled(ItemSection)`
  border: 2px solid ${({ theme }) => theme.greyColor20};
  box-sizing: border-box;
  border-radius: 8px;
  padding: 0 20px;
  margin-top: 41px;
`;

const GroupLabel = styled(Label)`
  width: auto;
  margin-right: 8px;
  display: inline-block;
`;

const ConditionSection: React.FC<{ formField: FormConditionItem }> = ({
  formField,
}) => {
  const { widgetsInfo, setUiWidgetsInfo } = useServiceForm();

  const currentlySelectedCondition =
    widgetsInfo[formField.fieldName]?.selectedItem;

  const label = formField.title || formField.fieldKey;

  return (
    <FormItemGroup key={`form-field-group-${formField.fieldKey}`}>
      <FormItemGroupDropDown key={`form-field-${formField.fieldKey}`}>
        {label ? <GroupLabel>{label}:</GroupLabel> : null}
        <DropDown
          data={Object.keys(formField.conditions).map((dataItem) => ({
            text: dataItem,
            value: dataItem,
          }))}
          onSelect={(selectedItem) =>
            setUiWidgetsInfo(formField.fieldName, {
              selectedItem: selectedItem.value,
            })
          }
          value={currentlySelectedCondition}
        />
      </FormItemGroupDropDown>
      <FormSection
        blocks={[formField.conditions[currentlySelectedCondition]]}
      />
    </FormItemGroup>
  );
};

const FormSection: React.FC<{ blocks: FormBlock[] }> = (props) => {
  const { blocks } = props;

  return (
    <>
      {blocks.map((formField) => {
        if (formField._type === "formGroup") {
          return <FormSection blocks={formField.properties} />;
        }

        if (formField._type === "formCondition") {
          return <ConditionSection formField={formField} />;
        }

        return (
          <ItemSection key={`form-field-${formField.fieldKey}`}>
            <Property property={formField} />
          </ItemSection>
        );
      })}
    </>
  );
};

export { FormSection };
