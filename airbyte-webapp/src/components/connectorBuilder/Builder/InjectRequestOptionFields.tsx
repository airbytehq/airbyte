import { useField } from "formik";

import { RequestOption } from "core/request/ConnectorManifest";

import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { injectIntoValues } from "../types";

interface InjectRequestOptionFieldsProps {
  path: string;
  descriptor: string;
  excludeInjectIntoValues?: string[];
}

export const InjectRequestOptionFields: React.FC<InjectRequestOptionFieldsProps> = ({
  path,
  descriptor,
  excludeInjectIntoValues,
}) => {
  const [field, , helpers] = useField<RequestOption>(path);

  return (
    <>
      <BuilderField
        type="enum"
        path={`${path}.inject_into`}
        options={
          excludeInjectIntoValues
            ? injectIntoValues.filter((val) => !excludeInjectIntoValues.includes(val))
            : injectIntoValues
        }
        onChange={(newValue) => {
          if (newValue === "path") {
            helpers.setValue({ inject_into: newValue, field_name: undefined, type: "RequestOption" });
          }
        }}
        label="Inject into"
        tooltip={`Configures where the ${descriptor} should be set on the HTTP requests`}
      />
      {field.value.inject_into !== "path" && (
        <BuilderFieldWithInputs
          type="string"
          path={`${path}.field_name`}
          label="Field name"
          tooltip={`Configures which key should be used in the location that the ${descriptor} is being injected into`}
        />
      )}
    </>
  );
};
