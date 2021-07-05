import React from "react";
import { SyncSchemaField } from "core/domain/catalog";

const Rows: React.FC<{
  fields: SyncSchemaField[];
  children: (field: SyncSchemaField) => React.ReactNode;
}> = (props) => (
  <>
    {props.fields.map((field) => (
      <React.Fragment key={field.key}>
        {props.children(field)}
        {field.fields && <Rows fields={field.fields}>{props.children}</Rows>}
      </React.Fragment>
    ))}
  </>
);

export { Rows };
