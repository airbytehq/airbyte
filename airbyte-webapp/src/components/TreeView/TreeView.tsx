import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "../../components";
import TreeViewRow from "./components/TreeViewRow";
import {
  SyncSchema,
  AirbyteStreamConfiguration
} from "../../core/domain/catalog";

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
  const sortedSchema = useMemo(
    () => ({
      streams: schema.streams.sort((o1, o2) =>
        compareByName(o1.stream, o2.stream)
      )
    }),
    [schema.streams]
  );

  const onUpdateItem = useCallback(
    (streamId: string, newStream: Partial<AirbyteStreamConfiguration>) => {
      const newSchema = sortedSchema.streams.map(streamNode => {
        return streamNode.stream.name === streamId
          ? {
              ...streamNode,
              config: { ...streamNode.config, ...newStream }
            }
          : streamNode;
      });

      onChangeSchema({ streams: newSchema });
    },
    [sortedSchema, onChangeSchema]
  );

  const hasSelectedItem = useMemo(
    () => sortedSchema.streams.some(streamNode => streamNode.config.selected),
    [sortedSchema.streams]
  );

  const onCheckAll = useCallback(() => {
    const allSelectedValues = !hasSelectedItem;

    const newSchema = sortedSchema.streams.map(streamNode => {
      return {
        ...streamNode,
        config: { ...streamNode.config, selected: allSelectedValues }
      };
    });

    onChangeSchema({ streams: newSchema });
  }, [hasSelectedItem, onChangeSchema, sortedSchema.streams]);

  return (
    <div>
      <SelectButton onClick={onCheckAll} type="button">
        {hasSelectedItem ? (
          <FormattedMessage id="sources.schemaUnselectAll" />
        ) : (
          <FormattedMessage id="sources.schemaSelectAll" />
        )}
      </SelectButton>
      {sortedSchema.streams.map(stream => (
        <TreeViewRow
          key={stream.stream.name}
          streamNode={stream}
          updateItem={onUpdateItem}
        />
      ))}
    </div>
  );
};

export default TreeView;
