import React from "react";

import { DropDown, Input } from "components";
import { Field, FieldProps } from "formik";

const NamespaceField: React.FC<{}> = ({}) => {
  return (
    <>
      <Field name="namespaceDefinition">
        {({ field, form }: FieldProps<string>) => (
          <>
            <DropDown
              data={[
                {
                  value: "source",
                  text: "source",
                },
                {
                  value: "destination",
                  text: "destination",
                },
                {
                  value: "custom",
                  text: "custom",
                },
              ]}
              value={field.value}
              onChange={({ value }) => form.setFieldValue(field.name, value)}
            />
            {field.value === "custom" && (
              <Field name="namespaceFormat" component={Input} />
            )}
          </>
        )}
      </Field>
    </>
  );
};

export { NamespaceField };
