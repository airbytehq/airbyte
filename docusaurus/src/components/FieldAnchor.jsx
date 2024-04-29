import React from "react";

/**
 * FieldAnchor is a dummy-component in the docusaurus build but is used when the documentation is rendered in the webapp
 * to be able to highlight the relevant section for a focused field in the form next to the documentation.
 * 
 * The "field" property has to be set to the field name in the form the section should be connected to: <FieldAnchor field="replication_method.replication_slot" />
 * For oneOf fields, the selected mode has to be specified in square brackets:  <FieldAnchor field="replication_method[CDC]" />
 * It's possible to list multiple fields separated by comma: <FieldAnchor field="replication_method.replication_slot,replication_method.queue_size" />
 */
export const FieldAnchor = ({ children }) => {
  return <div>{children}</div>;
};