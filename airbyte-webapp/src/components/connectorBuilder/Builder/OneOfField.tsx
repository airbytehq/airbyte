import { useField } from "formik";
import { useState } from "react";

import { ListBox } from "components/ui/ListBox";

interface OneOfFieldProps {
  options: Array<{ label: string; value: string }>;
  path: string;
}

export const OneOfField: React.FC<OneOfFieldProps> = ({ options, path }) => {
  const pathPlusType = `${path}.type`;
  const [, , helpers] = useField(pathPlusType);
  const [value, setValue] = useState(options[0].value);

  return (
    <ListBox
      options={options}
      selectedValue={value}
      onSelect={(selectedValue) => {
        setValue(selectedValue);
        helpers.setValue(selectedValue);
      }}
    />
  );
};
