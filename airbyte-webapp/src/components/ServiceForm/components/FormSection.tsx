import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { DropDown, Label, VariableInput } from "components";
import {
  FormBlock,
  FormConditionItem,
  FormObjectArrayItem,
} from "core/form/types";
import { PropertySection } from "./PropertySection";
import { useServiceForm } from "../serviceFormContext";
import GroupControls from "./Property/GroupControls";

const ItemContainer = styled.div`
  margin-bottom: 27px;
`;

const GroupLabel = styled(Label)`
  width: auto;
  margin-right: 8px;
  display: inline-block;
`;

const ConditionControls = styled.div`
  padding-top: 25px;
`;

const ConditionSection: React.FC<{ formField: FormConditionItem }> = ({
  formField,
}) => {
  const { widgetsInfo, setUiWidgetsInfo } = useServiceForm();

  const currentlySelectedCondition =
    widgetsInfo[formField.fieldName]?.selectedItem;

  const label = formField.title || formField.fieldKey;

  return (
    <GroupControls
      key={`form-field-group-${formField.fieldKey}`}
      title={
        <>
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
        </>
      }
    >
      <ConditionControls>
        <FormSection
          blocks={[formField.conditions[currentlySelectedCondition]]}
        />
      </ConditionControls>
    </GroupControls>
  );
};

const ArraySection: React.FC<{ formField: FormObjectArrayItem }> = ({
  formField,
}) => {
  const [editingItem, setItemEdit] = useState<number | null>(null);
  // const { addUnfinishedFlow, removeUnfinishedFlow } = useServiceForm();

  return (
    <GroupControls
      key={`form-variable-fields-${formField?.fieldKey}`}
      title={<FormattedMessage id="form.customReports" />}
    >
      <ItemContainer>
        <VariableInput
          isEditMode={editingItem !== null}
          onStartEdit={(n) => setItemEdit(n)}
          onDone={() => setItemEdit(null)}
          onCancelEdit={() => setItemEdit(null)}
          items={[]}
        >
          <FormSection blocks={[formField.properties]} />
        </VariableInput>
      </ItemContainer>
    </GroupControls>
  );
};

const FormSection: React.FC<{ blocks: FormBlock[] }> = ({ blocks }) => {
  return (
    <>
      {blocks.map((formField) => {
        if (formField._type === "formGroup") {
          return (
            <FormSection
              key={formField.fieldName}
              blocks={formField.properties}
            />
          );
        }

        if (formField._type === "formCondition") {
          return (
            <ConditionSection key={formField.fieldName} formField={formField} />
          );
        }

        if (formField._type === "objectArray") {
          return (
            <ArraySection key={formField.fieldName} formField={formField} />
          );
        }

        return (
          <ItemContainer key={`form-field-${formField.fieldKey}`}>
            <PropertySection property={formField} />
          </ItemContainer>
        );
      })}
    </>
  );
};

export { FormSection };
