import React from "react";
import { FormattedMessage } from "react-intl";

import { Popout } from "components/ui/Popout";
import { Tooltip } from "components/ui/Tooltip";

import { Path } from "core/domain/catalog";

import styles from "./PathPopout.module.scss";
import { PathPopoutButton } from "./PathPopoutButton";

export function pathDisplayName(path: Path): string {
  return path.join(".");
}

export type IndexerType = null | "required" | "sourceDefined";

interface PathPopoutBaseProps {
  paths: Path[];
  pathType: "required" | "sourceDefined";
  placeholder?: React.ReactNode;
  id?: string;
}

interface PathMultiProps {
  path?: Path[];
  onPathChange: (pkPath: Path[]) => void;
  isMulti: true;
}

interface PathProps {
  path?: Path;
  onPathChange: (pkPath: Path) => void;
  isMulti?: false;
}

type PathPopoutProps = PathPopoutBaseProps & (PathMultiProps | PathProps);

export const PathPopout: React.FC<PathPopoutProps> = (props) => {
  const pathPopoutId = `${props.id}_pathPopout`;

  if (props.pathType === "sourceDefined") {
    if (props.path && props.path.length > 0) {
      const text = props.isMulti ? props.path.map(pathDisplayName).join(", ") : pathDisplayName(props.path);

      return (
        <Tooltip
          placement="bottom-start"
          control={
            <div className={styles.text} data-testid={`${pathPopoutId}_text`}>
              {text}
            </div>
          }
        >
          {text}
        </Tooltip>
      );
    }

    return <FormattedMessage id="connection.catalogTree.sourceDefined" />;
  }

  const text = props.path
    ? props.isMulti
      ? props.path.map(pathDisplayName).join(", ")
      : pathDisplayName(props.path)
    : "";

  const options = props.paths.map((path) => ({
    value: path,
    label: pathDisplayName(path),
  }));

  return (
    <Popout
      options={options}
      value={props.path}
      isMulti={props.isMulti}
      isSearchable
      onChange={(options: PathPopoutProps["isMulti"] extends true ? Array<{ value: Path }> : { value: Path }) => {
        const finalValues = Array.isArray(options) ? options.map((op) => op.value) : options.value;

        props.onPathChange(finalValues);
      }}
      placeholder={props.placeholder}
      components={props.isMulti ? { MultiValue: () => null } : undefined}
      id={pathPopoutId}
      targetComponent={({ onOpen }) => (
        <PathPopoutButton
          items={props.isMulti ? props.path?.map(pathDisplayName) : props.path}
          onClick={onOpen}
          testId={pathPopoutId}
        >
          {text}
        </PathPopoutButton>
      )}
    />
  );
};
