import React from "react";
import styled from "styled-components";

import { DropDown, Label, ArrayOfObjectsEditor } from "components";
import {
  FormBlock,
  FormConditionItem,
  FormObjectArrayItem,
} from "core/form/types";
import { PropertySection } from "./PropertySection";
import { useServiceForm } from "../serviceFormContext";
import GroupControls from "./Property/GroupControls";
import { FieldArray, useField } from "formik";

const SectionContainer = styled.div`
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

const ConditionSection: React.FC<{
  formField: FormConditionItem;
  path?: string;
}> = ({ formField, path }) => {
  const { widgetsInfo, setUiWidgetsInfo } = useServiceForm();

  const currentlySelectedCondition = widgetsInfo[formField.path]?.selectedItem;

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
              setUiWidgetsInfo(formField.path, {
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
          blocks={formField.conditions[currentlySelectedCondition]}
          path={path}
          skipAppend
        />
      </ConditionControls>
    </GroupControls>
  );
};

const ArraySection: React.FC<{
  formField: FormObjectArrayItem;
  path: string;
}> = ({ formField, path }) => {
  const {
    addUnfinishedFlow,
    removeUnfinishedFlow,
    unfinishedFlows,
  } = useServiceForm();
  const [field, , form] = useField(path);

  const items = field.value ?? [];
  const flow = unfinishedFlows[path];

  return (
    <GroupControls
      key={`form-variable-fields-${formField?.fieldKey}`}
      title={formField.title || formField.fieldKey}
    >
      <SectionContainer>
        <FieldArray
          name={path}
          render={(arrayHelpers) => (
            <ArrayOfObjectsEditor
              isEditMode={!!flow}
              onStartEdit={(index) =>
                addUnfinishedFlow(path, {
                  id: index,
                  startValue: index < items.length ? items[index] : null,
                })
              }
              onDone={() => removeUnfinishedFlow(path)}
              onCancelEdit={() => {
                removeUnfinishedFlow(path);

                if (flow.startValue) {
                  form.setValue(flow.startValue);
                }
              }}
              onRemove={arrayHelpers.remove}
              items={items}
            >
              {() => (
                <FormSection
                  blocks={formField.properties}
                  path={`${path}.${flow.id}`}
                  skipAppend
                />
              )}
            </ArrayOfObjectsEditor>
          )}
        />
      </SectionContainer>
    </GroupControls>
  );
};

const FormSection: React.FC<{
  blocks: FormBlock[] | FormBlock;
  path?: string;
  skipAppend?: boolean;
}> = ({ blocks, path, skipAppend }) => {
  const sections = Array.isArray(blocks) ? blocks : [blocks];
  return (
    <>
      {sections.map((formField) => {
        const sectionPath = path
          ? skipAppend
            ? path
            : `${path}.${formField.fieldKey}`
          : formField.fieldKey;

        if (formField._type === "formGroup") {
          return (
            <FormSection
              key={sectionPath}
              blocks={formField.properties}
              path={sectionPath}
            />
          );
        }

        if (formField._type === "formCondition") {
          return (
            <ConditionSection
              key={sectionPath}
              formField={formField}
              path={sectionPath}
            />
          );
        }

        if (formField._type === "objectArray") {
          return (
            <ArraySection
              key={sectionPath}
              formField={formField}
              path={sectionPath}
            />
          );
        }

        return (
          <SectionContainer key={`form-field-${formField.fieldKey}`}>
            <PropertySection property={formField} path={sectionPath} />
          </SectionContainer>
        );
      })}
    </>
  );
};

export { FormSection };
