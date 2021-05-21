import React from "react";
// import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { FieldArray, useField } from "formik";

import GroupControls from "components/GroupControls";
import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";
import TransformationItem from "./TransformationItem";

const TransformationBlock: React.FC = () => {
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
            // TODO: add real actions
            onStartEdit={() => console.log("onStartEdit")}
            onCancelEdit={() => console.log("onCancelEdit")}
            onDone={() => console.log("onDone")}
            isEditMode
          >
            {() => <TransformationItem />}
          </ArrayOfObjectsEditor>
        )}
      />
    </GroupControls>
  );
};

export default TransformationBlock;
