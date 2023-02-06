import { FieldArray, useField } from "formik";
import React, { useMemo, useState } from "react";

import { ArrayOfObjectsEditor } from "components";
import GroupControls from "components/GroupControls";
import { TooltipTable } from "components/ui/Tooltip";

import { FormBlock, FormGroupItem, FormObjectArrayItem } from "core/form/types";

import { GroupLabel } from "./GroupLabel";
import { SectionContainer } from "./SectionContainer";
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
  const [field, , fieldHelper] = useField<Array<Record<string, string>>>(path);
  const [editIndex, setEditIndex] = useState<number | undefined>();
  // keep the previous state of the currently edited item around so it can be restored on cancelling the form
  const [originalItem, setOriginalItem] = useState<Record<string, string> | undefined>();

  const items: Array<Record<string, string>> = useMemo(() => field.value ?? [], [field.value]);

  // keep the list of rendered items stable as long as editing is in progress
  const itemsWithOverride = useMemo(() => {
    if (typeof editIndex === "undefined") {
      return items;
    }
    return items.map((item, index) => (index === editIndex ? originalItem : item)).filter(Boolean) as Array<
      Record<string, string>
    >;
  }, [editIndex, originalItem, items]);

  const { renderItemName, renderItemDescription } = useMemo(() => {
    const { properties } = formField.properties as FormGroupItem;

    const details = itemsWithOverride.map((item: Record<string, string>) => {
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
  }, [itemsWithOverride, formField.properties]);

  const clearEditIndex = () => setEditIndex(undefined);

  // on cancelling editing, either remove the item if it has been a new one or put back the old value in the form
  const onCancel = () => {
    const newList = [...field.value];
    if (!originalItem) {
      newList.pop();
    } else if (editIndex !== undefined && originalItem) {
      newList.splice(editIndex, 1, originalItem);
    }

    fieldHelper.setValue(newList);
    clearEditIndex();
  };

  return (
    <SectionContainer>
      <GroupControls
        name={path}
        key={`form-variable-fields-${formField?.fieldKey}`}
        label={<GroupLabel formField={formField} />}
      >
        <FieldArray
          name={path}
          render={(arrayHelpers) => (
            <ArrayOfObjectsEditor
              editableItemIndex={editIndex}
              onStartEdit={(n) => {
                setEditIndex(n);
                setOriginalItem(items[n]);
              }}
              onRemove={arrayHelpers.remove}
              onCancel={onCancel}
              items={itemsWithOverride}
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
                  onDone={clearEditIndex}
                  onCancel={onCancel}
                />
              )}
            />
          )}
        />
      </GroupControls>
    </SectionContainer>
  );
};
