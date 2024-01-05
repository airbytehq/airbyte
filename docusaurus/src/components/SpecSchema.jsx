import React from "react";
import JSONSchemaViewer from "@theme/JSONSchemaViewer"

export const SpecSchema = ({
  specJSON
}) => {
  const spec = JSON.parse(specJSON);
  spec.description = undefined;
  spec.title = "Config fields";
  return <>
    <JSONSchemaViewer schema={spec} />
  </>;
};