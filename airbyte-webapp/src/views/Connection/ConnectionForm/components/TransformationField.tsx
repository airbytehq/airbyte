import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { FieldArray } from "formik";

import GroupControls from "components/GroupControls";
import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";
import TransformationItem from "./TransformationItem";
import { OperatorType, Transformation } from "core/domain/connector/operation";
import { isDefined } from "utils/common";
import { FormikProps } from "formik/dist/types";
import { ArrayHelpers } from "formik/dist/FieldArray";

const DefaultOperation: Transformation = {
  name: "My dbt transformations",
  operatorConfiguration: {
    operatorType: OperatorType.Dbt,
    dbt: {
      dockerImage: "fishtownanalytics/dbt:0.19.1",
      dbtArguments: "run",
    },
  },
};

const TransformationField: React.FC = () => {
  const [editableItemIdx, setEditableItem] = useState<number | null>(null);
  return (
    <GroupControls title={<FormattedMessage id="form.customTransformation" />}>
      <FieldArray
        name="transformations"
        render={({
          remove,
          push,
          replace,
          form,
        }: ArrayHelpers & {
          form: FormikProps<{ transformations: Transformation[] }>;
          name: string;
        }) => (
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
              <TransformationItem
                transformation={editableItem ?? DefaultOperation}
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
        )}
      />
    </GroupControls>
  );
};

export { TransformationField };
