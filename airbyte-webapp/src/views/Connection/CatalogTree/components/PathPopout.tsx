import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { Popout } from "components";

import { Path } from "core/domain/catalog";

import Tooltip from "./Tooltip";

export function pathDisplayName(path: Path): string {
  return path.join(".");
}

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  color: ${({ theme }) => theme.greyColor40};
  margin-left: 6px;
  transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
  transition: 0.3s;
  vertical-align: sub;
`;

export type IndexerType = null | "required" | "sourceDefined";

type PathPopoutProps = {
  paths: Path[];
  pathType: "required" | "sourceDefined";
  placeholder?: React.ReactNode;
} & (PathMultiProps | PathProps);

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
        <div onClick={onOpen}>
          {text}
          <Arrow icon={faSortDown} />
          <Tooltip items={props.isMulti ? props.path?.map(pathDisplayName) : props.path} />
        </div>
      )}
    />
  );
};
