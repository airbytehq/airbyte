import classNames from "classnames";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import styles from "./BuilderTitle.module.scss";

interface BuilderTitleProps {
  // path to the location in the Connector Manifest schema which should be set by this component
  path: string;
  label: string;
  size: "md" | "lg";
}

export const BuilderTitle: React.FC<BuilderTitleProps> = ({ path, label, size }) => {
  const [field, meta] = useField(path);
  const hasError = !!meta.error && meta.touched;

  return (
    <div className={styles.container}>
      <Text className={styles.label} size="xs">
        {label}
      </Text>
      <Input
        containerClassName={classNames(styles.inputContainer, {
          [styles.md]: size === "md",
          [styles.lg]: size === "lg",
        })}
        className={classNames(styles.input, { [styles.md]: size === "md", [styles.lg]: size === "lg" })}
        {...field}
        type="text"
        value={field.value ?? ""}
        error={hasError}
      />
      {hasError && (
        <Text size="xs" className={styles.error}>
          <FormattedMessage id={meta.error} />
        </Text>
      )}
    </div>
  );
};
