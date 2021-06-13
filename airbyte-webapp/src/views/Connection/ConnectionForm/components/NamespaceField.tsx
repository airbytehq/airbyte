import React from "react";
import { Field, FieldProps } from "formik";

import { DropDown, Input } from "components";
import { ConnectionNamespaceDefinition } from "core/domain/connection";

const NamespaceField: React.FC<{}> = ({}) => {
  return (
    <>
      <Field name="namespaceDefinition">
        {({ field, form }: FieldProps<string>) => (
          <>
            <DropDown
              data={[
                {
                  value: ConnectionNamespaceDefinition.Source,
                  text: "source",
                },
                {
                  value: ConnectionNamespaceDefinition.Destination,
                  text: "destination",
                },
                {
                  value: ConnectionNamespaceDefinition.CustomFormat,
                  text: "custom",
                },
              ]}
              value={field.value}
              onChange={({ value }) => form.setFieldValue(field.name, value)}
            />
            {field.value === ConnectionNamespaceDefinition.CustomFormat && (
              <Field name="namespaceFormat" component={Input} />
            )}
          </>
        )}
      </Field>
    </>
  );
};

export { NamespaceField };
