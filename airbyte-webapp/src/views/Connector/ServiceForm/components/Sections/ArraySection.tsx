import { FieldArray, useField } from "formik";
import React, { useMemo, useState } from "react";

import { ArrayOfObjectsEditor } from "components";
import GroupControls from "components/GroupControls";

import { FormBlock, FormGroupItem, FormObjectArrayItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { SectionContainer } from "./common";
import { VariableInputFieldForm } from "./VariableInputFieldForm";

interface ArraySectionProps {
  formField: FormObjectArrayItem;
  path: string;
  disabled?: boolean;
}

const getItemName = (item: Record<string, string>): string => {
  return Object.keys(item)
    .sort()
    .map((key) => `${key}: ${item[key]}`)
    .join(" | ");
};

const getItemDescription = (item: Record<string, string>, properties: FormBlock[]): React.ReactNode => {
  const rows = Object.keys(item)
    .sort()
    .map((key) => {
      const property = properties.find(({ fieldKey }) => fieldKey === key);
      const name = property?.title ?? key;
      const value = item[key];
      return (
        <tr key={key}>
          <td style={{ paddingRight: 10 }}>{name}:</td>
          <td>{value}</td>
        </tr>
      );
    });

  return (
    <table>
      <tbody>{rows}</tbody>
    </table>
  );
};

export const ArraySection: React.FC<ArraySectionProps> = ({ formField, path, disabled }) => {
  const { addUnfinishedFlow, removeUnfinishedFlow, unfinishedFlows } = useServiceForm();

  const [field, , fieldHelper] = useField(path);
  const [editIndex, setEditIndex] = useState<number>();

  const items = useMemo(() => field.value ?? [], [field.value]);

  const { renderItemName, renderItemDescription } = useMemo(() => {
    const { properties } = formField.properties as FormGroupItem;

    const details = items.map((item: Record<string, string>) => {
      const name = getItemName(item);
      const description = getItemDescription(item, properties);
      return {
        name,
        description,
      };
    });

    return {
      renderItemName: (_: unknown, index: number) => details[index].name,
      renderItemDescription: (_: unknown, index: number) => details[index].description,
    };
  }, [items, formField.properties]);

  const unfinishedFlow = unfinishedFlows[path];

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
              editableItemIndex={editIndex}
              onStartEdit={(index) => {
                setEditIndex(index);
                addUnfinishedFlow(path, {
                  id: index,
                  startValue: index < items.length ? items : null,
                });
              }}
              onRemove={arrayHelpers.remove}
              items={items}
              renderItemName={renderItemName}
              renderItemDescription={renderItemDescription}
              disabled={disabled}
              editModalSize="sm"
            >
              {(item) => (
                <VariableInputFieldForm
                  formField={formField}
                  path={`hidden.${path}`}
                  disabled={disabled}
                  item={item}
                  onDone={(updatedItem) => {
                    // Edit or Create
                    const updatedValue = unfinishedFlow.startValue
                      ? items.map((item: unknown, index: number) => (index === editIndex ? updatedItem : item))
                      : [...items, updatedItem];

                    fieldHelper.setValue(updatedValue);
                    removeUnfinishedFlow(path);
                    setEditIndex(undefined);
                  }}
                  onCancel={() => {
                    if (unfinishedFlow.startValue) {
                      fieldHelper.setValue(unfinishedFlow.startValue);
                    }
                    removeUnfinishedFlow(path);
                    setEditIndex(undefined);
                  }}
                />
              )}
            </ArrayOfObjectsEditor>
          )}
        />
      </SectionContainer>
    </GroupControls>
  );
};
