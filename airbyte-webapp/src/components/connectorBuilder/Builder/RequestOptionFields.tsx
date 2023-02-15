import { useField } from "formik";

import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { injectIntoValues, RequestOptionOrPathInject } from "../types";

interface RequestOptionFieldsProps {
  path: string;
  descriptor: string;
  excludePathInjection?: boolean;
}

export const RequestOptionFields: React.FC<RequestOptionFieldsProps> = ({ path, descriptor, excludePathInjection }) => {
  const [field, , helpers] = useField<RequestOptionOrPathInject>(path);

  return (
    <>
      <BuilderField
        type="enum"
        path={`${path}.inject_into`}
        options={excludePathInjection ? injectIntoValues.filter((target) => target !== "path") : injectIntoValues}
        onChange={(newValue) => {
          if (newValue === "path") {
            helpers.setValue({ inject_into: newValue });
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
