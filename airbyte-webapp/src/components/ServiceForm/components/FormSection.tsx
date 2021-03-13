import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { DropDown, Label, VariableInput } from "components";
import { FormBlock, FormConditionItem } from "core/form/types";
import { Property } from "./Property";
import { useServiceForm } from "../serviceFormContext";
import GroupControls from "./Property/GroupControls";

const ItemSection = styled.div`
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

// TODO: fix form in component
const VariableSection: React.FC<{ formField?: FormConditionItem }> = ({
  formField,
}) => {
  return (
    <GroupControls
      key={`form-variable-fields-${formField?.fieldKey}`}
      title={<FormattedMessage id="form.customReports" />}
    >
      <ItemSection>
        <VariableInput items={[]}>FORM IS HERE</VariableInput>
      </ItemSection>
    </GroupControls>
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

  // TODO: return in right condition
  return <VariableSection />;
};

export { FormSection };
