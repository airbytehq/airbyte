import { FieldArray, useField } from "formik";
import React, { useMemo, useState } from "react";

import { ArrayOfObjectsEditor } from "components";
import GroupControls from "components/GroupControls";
import { TooltipTable } from "components/ui/Tooltip";

import { FormBlock, FormGroupItem, FormObjectArrayItem } from "core/form/types";

import { GroupLabel } from "./GroupLabel";
import { VariableInputFieldForm } from "./VariableInputFieldForm";

interface ArraySectionProps {
  formField: FormObjectArrayItem;
  path: string;
  disabled?: boolean;
}

const getItemName = (item: Record<string, string>, properties: FormBlock[]): string => {
  return Object.keys(item)
    .sort()
    .map((key) => {
      const property = properties.find(({ fieldKey }) => fieldKey === key);
      const name = property?.title ?? key;
      return `${name}: ${item[key]}`;
    })
    .join(" | ");
};

const getItemDescription = (item: Record<string, string>, properties: FormBlock[]): React.ReactNode => {
  const rows = Object.keys(item)
    .sort()
    .map((key) => {
      const property = properties.find(({ fieldKey }) => fieldKey === key);
      const name = property?.title ?? key;
      const value = item[key];
      return [name, value];
    });

  return <TooltipTable rows={rows} />;
};

export const ArraySection: React.FC<ArraySectionProps> = ({ formField, path, disabled }) => {
  const [field, , fieldHelper] = useField(path);
  const [editIndex, setEditIndex] = useState<number>();

  const items = useMemo(() => field.value ?? [], [field.value]);

  const { renderItemName, renderItemDescription } = useMemo(() => {
    const { properties } = formField.properties as FormGroupItem;

    const details = items.map((item: Record<string, string>) => {
      const name = getItemName(item, properties);
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

  const clearEditIndex = () => setEditIndex(undefined);

  return (
    <GroupControls
      name={path}
      key={`form-variable-fields-${formField?.fieldKey}`}
      title={<GroupLabel formField={formField} />}
    >
      <FieldArray
        name={path}
        render={(arrayHelpers) => (
          <ArrayOfObjectsEditor
            editableItemIndex={editIndex}
            onStartEdit={setEditIndex}
            onRemove={arrayHelpers.remove}
            onCancel={clearEditIndex}
            items={items}
            renderItemName={renderItemName}
            renderItemDescription={renderItemDescription}
            disabled={disabled}
            editModalSize="sm"
            renderItemEditorForm={(item) => (
              <VariableInputFieldForm
                formField={formField}
                path={`${path}[${editIndex ?? 0}]`}
                disabled={disabled}
                item={item}
                onDone={(updatedItem) => {
                  const updatedValue =
                    editIndex !== undefined && editIndex < items.length
                      ? items.map((item: unknown, index: number) => (index === editIndex ? updatedItem : item))
                      : [...items, updatedItem];

                  fieldHelper.setValue(updatedValue);
                  clearEditIndex();
                }}
                onCancel={clearEditIndex}
              />
            )}
          />
        )}
      />
    </GroupControls>
  );
};
