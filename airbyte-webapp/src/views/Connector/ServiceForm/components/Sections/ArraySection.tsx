import React from "react";
import { FieldArray, useField } from "formik";

import { ArrayOfObjectsEditor } from "components";

import { FormObjectArrayItem } from "core/form/types";
import { useServiceForm } from "../../serviceFormContext";
import GroupControls from "components/GroupControls";
import { FormSection } from "./FormSection";
import { SectionContainer } from "./common";

/**
 * ArraySection is responsible for handling array of objects
 * @param formField
 * @param path
 * @constructor
 */
export const ArraySection: React.FC<{
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
                  startValue: index < items.length ? items : null,
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
