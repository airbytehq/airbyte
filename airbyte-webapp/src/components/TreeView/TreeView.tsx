import React, { useCallback, useMemo } from "react";

import { TreeViewSection } from "./components/TreeViewSection";
import { SyncSchema, AirbyteStreamConfiguration } from "core/domain/catalog";

type IProps = {
  schema: SyncSchema;
  onChangeSchema: (schema: SyncSchema) => void;
};

function compareByName<T extends { name: string }>(o1: T, o2: T): -1 | 0 | 1 {
  if (o1.name === o2.name) {
    return 0;
  }
  return o1.name > o2.name ? 1 : -1;
}

const TreeView: React.FC<IProps> = ({ schema, onChangeSchema }) => {
  const onUpdateItem = useCallback(
    (streamId: string, newStream: Partial<AirbyteStreamConfiguration>) => {
      const newSchema = schema.streams.map((streamNode) => {
        return streamNode.stream.name === streamId
          ? {
              ...streamNode,
              config: { ...streamNode.config, ...newStream },
            }
          : streamNode;
      });

      onChangeSchema({ streams: newSchema });
    },
    [schema, onChangeSchema]
  );

  // TODO: there is no need to sort schema everytime. We need to do it only once as streams[].stream is const
  const sortedSchema = useMemo(
    () => ({
      streams: schema.streams.sort((o1, o2) =>
        compareByName(o1.stream, o2.stream)
      ),
    }),
    [schema.streams]
  );

  return (
    <>
      {sortedSchema.streams.map((streamNode) => (
        <TreeViewSection
          key={streamNode.stream.name}
          streamNode={streamNode}
          updateItem={onUpdateItem}
        />
      ))}
    </>
  );
};

export default TreeView;
