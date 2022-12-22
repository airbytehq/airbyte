import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { InfoText, INFO_TEXT_VARIANT_BY_PILL_VARIANT } from "components/ui/InfoText";
import { PillButtonVariant, PillSelect } from "components/ui/PillSelect";

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
  const SourceDefinedNode = useMemo(() => {
    if (props.path && props.path.length > 0) {
      return props.isMulti ? props.path.map(pathDisplayName).join(", ") : pathDisplayName(props.path);
    }
    return <FormattedMessage id="connection.catalogTree.sourceDefined" />;
  }, [props.isMulti, props.path]);

  if (props.pathType === "sourceDefined") {
    const variant = props.variant || "grey";
    return (
      <InfoText variant={INFO_TEXT_VARIANT_BY_PILL_VARIANT[variant]} className={styles.streamPathSelect}>
        {SourceDefinedNode}
      </InfoText>
    );
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
