import React from "react";
import { FormattedMessage } from "react-intl";

import { PillButtonVariant, PillSelect } from "components/ui/PillSelect";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { Path } from "core/domain/catalog";

import styles from "./StreamPathSelect.module.scss";

export const pathDisplayName = (path: Path): string => path.join(".");

export type IndexerType = null | "required" | "sourceDefined";

interface StreamPathSelectBaseProps {
  paths: Path[];
  pathType: IndexerType;
  placeholder?: React.ReactNode;
  variant?: PillButtonVariant;
  disabled?: boolean;
}

interface StreamPathSelectMultiProps {
  path?: Path[];
  onPathChange: (pkPath: Path[]) => void;
  isMulti: true;
}

interface StreamPathSelectProps {
  path?: Path;
  onPathChange: (pkPath: Path) => void;
  isMulti?: false;
}

type PathPopoutProps = StreamPathSelectBaseProps & (StreamPathSelectMultiProps | StreamPathSelectProps);

export const StreamPathSelect: React.FC<PathPopoutProps> = (props) => {
  if (props.pathType === "sourceDefined") {
    if (props.path && props.path.length > 0) {
      const text = props.isMulti ? props.path.map(pathDisplayName).join(", ") : pathDisplayName(props.path);

      return (
        <Text className={styles.text}>
          <Tooltip placement="bottom-start" control={text}>
            {text}
          </Tooltip>
        </Text>
      );
    }

    return <FormattedMessage id="connection.catalogTree.sourceDefined" />;
  }

  const options = props.paths.map((path) => ({
    value: path,
    label: pathDisplayName(path),
  }));

  return (
    <PillSelect
      disabled={props.disabled}
      variant={props.variant}
      options={options}
      value={props.path}
      isMulti={props.isMulti}
      onChange={(options: PathPopoutProps["isMulti"] extends true ? Array<{ value: Path }> : { value: Path }) => {
        const finalValues = Array.isArray(options) ? options.map((op) => op.value) : options.value;
        props.onPathChange(finalValues);
      }}
      className={styles.streamPathSelect}
    />
  );
};
