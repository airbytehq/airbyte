import React, { useCallback, useMemo } from "react";
import styled from "styled-components";
import { FieldArray, useField } from "formik";

import { ArrayOfObjectsEditor, DropDown, Label } from "components";
import {
  FormBlock,
  FormConditionItem,
  FormObjectArrayItem,
} from "core/form/types";
import { PropertySection } from "./PropertySection";
import { useServiceForm } from "../serviceFormContext";
import GroupControls from "components/GroupControls";
import { naturalComparator } from "utils/objects";
import { IDataItem } from "components/base/DropDown/components/Option";
import { AuthButton } from "./AuthButton";
import { WithFeature } from "hooks/services/Feature";

function OrderComparator(a: FormBlock, b: FormBlock): number {
  const aIsNumber = Number.isInteger(a.order);
  const bIsNumber = Number.isInteger(b.order);

  switch (true) {
    case aIsNumber && bIsNumber:
      return (a.order as number) - (b.order as number);
    case aIsNumber && !bIsNumber:
      return -1;
    case bIsNumber && !aIsNumber:
      return 1;
    default:
      return naturalComparator(a.fieldKey, b.fieldKey);
  }
}

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

  const options = useMemo(
    () =>
      Object.keys(formField.conditions).map((dataItem) => ({
        label: dataItem,
        value: dataItem,
      })),
    [formField.conditions]
  );
  const onOptionChange = useCallback(
    (selectedItem: IDataItem) =>
      setUiWidgetsInfo(formField.path, {
        selectedItem: selectedItem.value,
      }),
    [setUiWidgetsInfo, formField.path]
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
      name={path}
      key={`form-variable-fields-${formField?.fieldKey}`}
      title={formField.title || formField.fieldKey}
      description={formField.description}
    >
      <SectionContainer>
        <FieldArray
          name={path}
          render={(arrayHelpers) => (
            <ArrayOfObjectsEditor
              editableItemIndex={flow?.id}
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
  hasOauth?: boolean;
}> = ({ blocks = [], path, skipAppend, hasOauth }) => {
  const sections = useMemo(() => {
    const flattenedBlocks = [blocks].flat();

    if (flattenedBlocks.some((b) => Number.isInteger(b.order))) {
      return flattenedBlocks.sort(OrderComparator);
    }

    return flattenedBlocks;
  }, [blocks]);

  return (
    <>
      {hasOauth && (
        <WithFeature featureId="ALLOW_OAUTH_CONNECTOR">
          {
            <SectionContainer>
              <AuthButton />
            </SectionContainer>
          }
        </WithFeature>
      )}
      {sections
        .filter((formField) => !formField.airbyte_hidden)
        .map((formField) => {
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
                hasOauth={formField.hasOauth}
              />
            );
          } else if (formField._type === "formCondition") {
            return (
              <ConditionSection
                key={sectionPath}
                formField={formField}
                path={sectionPath}
              />
            );
          } else if (formField._type === "objectArray") {
            return (
              <ArraySection
                key={sectionPath}
                formField={formField}
                path={sectionPath}
              />
            );
          }

          if (formField.const !== undefined) {
            return null;
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
