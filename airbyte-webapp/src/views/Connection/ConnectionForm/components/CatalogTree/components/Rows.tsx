import React from "react";
import { SyncSchemaField } from "core/domain/catalog";

const Rows: React.FC<{
  fields: SyncSchemaField[];
  depth: number;
  children: (field: SyncSchemaField, depth: number) => React.ReactNode;
}> = (props) => (
  <>
    {props.fields.map((field) => (
      <React.Fragment key={field.key}>
        {props.children(field, props.depth)}
        {field.fields && (
          <Rows fields={field.fields} depth={props.depth}>
            {props.children}
          </Rows>
        )}
      </React.Fragment>
    ))}
  </>
);

export { Rows };
