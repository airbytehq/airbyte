import { useField } from "formik";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { DropDown } from "components/ui/DropDown";
import { Text } from "components/ui/Text";

import styles from "./BuilderField.module.scss";
import { BuilderStream } from "../types";

interface StreamReferenceFieldProps {
  // path to the location in the Connector Manifest schema which should be set by this component
  path: string;
  label: string;
  tooltip?: string;
  optional?: boolean;
  currentStreamIndex: number;
}

export const StreamReferenceField: React.FC<StreamReferenceFieldProps> = ({
  path,
  label,
  tooltip,
  optional,
  currentStreamIndex,
  ...props
}) => {
  const [streams] = useField<BuilderStream[]>("streams");
  const [field, meta, helpers] = useField(path);
  const hasError = !!meta.error && meta.touched;

  const options = useMemo(() => {
    return streams.value
      .filter((_value, index) => index !== currentStreamIndex)
      .map((stream) => ({
        value: stream.id,
        label: stream.name,
      }));
  }, [currentStreamIndex, streams.value]);

  return (
    <ControlLabels className={styles.container} label={label} infoTooltipContent={tooltip} optional={optional}>
      <DropDown
        {...props}
        options={options}
        onChange={(selected) => selected && helpers.setValue(selected.value)}
        value={field.value}
        error={hasError}
      />
      {hasError && (
        <Text className={styles.error}>
          <FormattedMessage id={meta.error} />
        </Text>
      )}
    </ControlLabels>
  );
};
