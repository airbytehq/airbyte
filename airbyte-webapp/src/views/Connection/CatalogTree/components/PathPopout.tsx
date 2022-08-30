import React from "react";

import { Popout } from "components";

import { Path } from "core/domain/catalog";

import { PathPopoutButton } from "./PathPopoutButton";

export function pathDisplayName(path: Path): string {
  return path.join(".");
}

export type IndexerType = null | "required" | "sourceDefined";

interface PathPopoutBaseProps {
  paths: Path[];
  pathType: "required" | "sourceDefined";
  placeholder?: React.ReactNode;
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
  if (props.pathType === "sourceDefined") {
    if (props.path) {
      const text = props.path
        ? props.isMulti
          ? props.path.map(pathDisplayName).join(", ")
          : pathDisplayName(props.path)
        : "";

      return <>{text}</>;
    }
    return <>{"<sourceDefined>"}</>;
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
      // @ts-expect-error need to solve issue with typings
      isMulti={props.isMulti}
      isSearchable
      onChange={(options: PathPopoutProps["isMulti"] extends true ? Array<{ value: Path }> : { value: Path }) => {
        const finalValues = Array.isArray(options) ? options.map((op) => op.value) : options.value;

        props.onPathChange(finalValues);
      }}
      placeholder={props.placeholder}
      components={props.isMulti ? { MultiValue: () => null } : undefined}
      targetComponent={({ onOpen }) => (
        <PathPopoutButton items={props.isMulti ? props.path?.map(pathDisplayName) : props.path} onClick={onOpen}>
          {text}
        </PathPopoutButton>
      )}
    />
  );
};
