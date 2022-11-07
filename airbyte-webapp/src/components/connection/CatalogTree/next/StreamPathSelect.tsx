import React from "react";
import { FormattedMessage } from "react-intl";

import { PillSelect } from "components/ui/PillSelect";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { Path } from "core/domain/catalog";

export const pathDisplayName = (path: Path): string => path.join(".");

export type IndexerType = null | "required" | "sourceDefined";

interface StreamPathSelectBaseProps {
  paths: Path[];
  pathType: "required" | "sourceDefined";
  placeholder?: React.ReactNode;
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
        <Tooltip placement="bottom-start" control={text}>
          <Text size="lg">{text}</Text>
        </Tooltip>
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
      options={options}
      value={props.path}
      isMulti={props.isMulti}
      onChange={(options: PathPopoutProps["isMulti"] extends true ? Array<{ value: Path }> : { value: Path }) => {
        const finalValues = Array.isArray(options) ? options.map((op) => op.value) : options.value;
        props.onPathChange(finalValues);
      }}
    />
  );
};
