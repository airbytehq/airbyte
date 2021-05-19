import React from "react";
// import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import GroupControls from "components/GroupControls";
import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";

const TransformationBlock: React.FC = () => {
  //TODO: add real data
  const transformations: { name: string }[] = [];

  return (
    <GroupControls title={<FormattedMessage id="form.customTransformation" />}>
      <ArrayOfObjectsEditor
        items={transformations}
        mainTitle={
          <FormattedMessage
            id="form.transformationCount"
            values={{ count: transformations.length }}
          />
        }
        addButtonText={<FormattedMessage id="form.addTransformation" />}
        // TODO: add real actions
        onStartEdit={() => console.log("onStartEdit")}
        onCancelEdit={() => console.log("onCancelEdit")}
        onDone={() => console.log("onDone")}
        onRemove={() => console.log("onRemove")}
        isEditMode={false}
      />
    </GroupControls>
  );
};

export default TransformationBlock;
