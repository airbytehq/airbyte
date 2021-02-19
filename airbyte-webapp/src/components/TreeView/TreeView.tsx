import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import TreeViewRow from "./components/TreeViewRow";
import { SyncSchema, AirbyteStreamConfiguration } from "core/domain/catalog";

type IProps = {
  schema: SyncSchema;
  onChangeSchema: (schema: SyncSchema) => void;
};

const SelectButton = styled(Button)`
  margin: 10px 17px 3px;
  padding: 3px;
  min-width: 90px;
`;

function compareByName<T extends { name: string }>(o1: T, o2: T): -1 | 0 | 1 {
  if (o1.name === o2.name) {
    return 0;
  }
  return o1.name > o2.name ? 1 : -1;
}

const TreeView: React.FC<IProps> = ({ schema, onChangeSchema }) => {
  const onUpdateItem = useCallback(
    (streamId: string, newStream: Partial<AirbyteStreamConfiguration>) => {
      const newSchema = schema.streams.map(streamNode => {
        return streamNode.stream.name === streamId
          ? {
              ...streamNode,
              config: { ...streamNode.config, ...newStream }
            }
          : streamNode;
      });

      onChangeSchema({ streams: newSchema });
    },
    [schema, onChangeSchema]
  );

  const hasSelectedItem = useMemo(
    () => schema.streams.some(streamNode => streamNode.config.selected),
    [schema.streams]
  );

  const onCheckAll = useCallback(() => {
    const allSelectedValues = !hasSelectedItem;

    const newSchema = schema.streams.map(streamNode => {
      return {
        ...streamNode,
        config: { ...streamNode.config, selected: allSelectedValues }
      };
    });

    onChangeSchema({ streams: newSchema });
  }, [hasSelectedItem, onChangeSchema, schema.streams]);

  // TODO: there is no need to sort schema everytime. We need to do it only once as streams[].stream is const
  const sortedSchema = useMemo(
    () => ({
      streams: schema.streams.sort((o1, o2) =>
        compareByName(o1.stream, o2.stream)
      )
    }),
    [schema.streams]
  );

  return (
    <div>
      <SelectButton onClick={onCheckAll} type="button">
        {hasSelectedItem ? (
          <FormattedMessage id="sources.schemaUnselectAll" />
        ) : (
          <FormattedMessage id="sources.schemaSelectAll" />
        )}
      </SelectButton>
      {sortedSchema.streams.map(streamNode => (
        <TreeViewRow
          key={streamNode.stream.name}
          streamNode={streamNode}
          updateItem={onUpdateItem}
        />
      ))}
    </div>
  );
};

export default TreeView;
