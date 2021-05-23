import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { FieldArray, useField } from "formik";

import GroupControls from "components/GroupControls";
import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";
import TransformationItem from "./TransformationItem";

type TransformationBlockProps = {
  onDone: () => void;
};
const TransformationBlock: React.FC<TransformationBlockProps> = ({
  onDone,
}) => {
  const [isEditMode, setIsEditMode] = useState(false);
  //TODO: add real data
  const [field, ,] = useField("transformations");
  const transformations = field.value ?? [];

  return (
    <GroupControls title={<FormattedMessage id="form.customTransformation" />}>
      <FieldArray
        name={"transformations"}
        render={(arrayHelpers) => (
          <ArrayOfObjectsEditor
            items={transformations}
            mainTitle={
              <FormattedMessage
                id="form.transformationCount"
                values={{ count: transformations.length }}
              />
            }
            addButtonText={<FormattedMessage id="form.addTransformation" />}
            doneButtonText={<FormattedMessage id="form.saveTransformation" />}
            onRemove={arrayHelpers.remove}
            onStartEdit={() => setIsEditMode(true)}
            onCancelEdit={() => setIsEditMode(false)}
            isEditMode={isEditMode}
            onDone={onDone}
          >
            {() => <TransformationItem />}
          </ArrayOfObjectsEditor>
        )}
      />
    </GroupControls>
  );
};

export default TransformationBlock;
