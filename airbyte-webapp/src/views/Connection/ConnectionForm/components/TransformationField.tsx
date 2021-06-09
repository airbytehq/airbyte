import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { ArrayHelpers, FormikProps } from "formik";

import TransformationForm from "views/Connection/TransformationForm";
import GroupControls from "components/GroupControls";
import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";
import { Transformation } from "core/domain/connection/operation";
import { isDefined } from "utils/common";

const TransformationField: React.FC<
  ArrayHelpers & {
    form: FormikProps<{ transformations: Transformation[] }>;
    defaultTransformation: Transformation;
  }
> = ({ remove, push, replace, form, defaultTransformation }) => {
  const [editableItemIdx, setEditableItem] = useState<number | null>(null);
  return (
    <GroupControls title={<FormattedMessage id="form.customTransformation" />}>
      <ArrayOfObjectsEditor
        items={form.values.transformations}
        editableItemIndex={editableItemIdx}
        mainTitle={
          <FormattedMessage
            id="form.transformationCount"
            values={{ count: form.values.transformations.length }}
          />
        }
        addButtonText={<FormattedMessage id="form.addTransformation" />}
        onRemove={remove}
        onStartEdit={(idx) => setEditableItem(idx)}
      >
        {(editableItem) => (
          <TransformationForm
            transformation={editableItem ?? defaultTransformation}
            onCancel={() => setEditableItem(null)}
            onDone={(transformation) => {
              if (isDefined(editableItemIdx)) {
                editableItemIdx >= form.values.transformations.length
                  ? push(transformation)
                  : replace(editableItemIdx, transformation);
                setEditableItem(null);
              }
            }}
          />
        )}
      </ArrayOfObjectsEditor>
    </GroupControls>
  );
};

export { TransformationField };
