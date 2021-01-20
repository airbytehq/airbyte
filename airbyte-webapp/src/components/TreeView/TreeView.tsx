import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Button from "../Button";
import TreeViewRow from "./components/TreeViewRow";
import { SyncSchemaStream, SyncSchema } from "../../core/resources/Schema";

type IProps = {
  schema: SyncSchema;
  onChangeSchema: (schema: SyncSchema) => void;
};

const SelectButton = styled(Button)`
  margin: 10px 17px 3px;
  padding: 3px;
  min-width: 90px;
`;

const TreeView: React.FC<IProps> = ({ schema, onChangeSchema }) => {
  const sortedSchema = {
    streams: schema.streams
      .sort((a, b) => (a.name > b.name ? 1 : -1))
      .map(item => ({
        ...item,
        fields: item.fields.sort((a, b) => (a.name > b.name ? 1 : -1))
      }))
  };

  const hasSelectedItem = useMemo(() => {
    return sortedSchema.streams.find(item => {
      if (item.selected) {
        return true;
      }

      return !!item.fields?.find(field => field.selected);
    });
  }, [sortedSchema.streams]);

  const onUpdateItem = (newItem: SyncSchemaStream) => {
    const newSchema = sortedSchema.streams.map(item => {
      if (item.name === newItem?.name) {
        return newItem;
      }

      return item;
    });

    onChangeSchema({ streams: newSchema });
  };

  const onCheckAll = useCallback(() => {
    const setSelectedValue = !hasSelectedItem;

    const newSchema = sortedSchema.streams.map(item => {
      if (!item.fields?.length) {
        return { ...item, selected: setSelectedValue };
      }

      const newFields = item.fields.map(field => ({
        ...field,
        selected: setSelectedValue
      }));
      return { ...item, fields: newFields };
    });

    onChangeSchema({ streams: newSchema });
  }, [hasSelectedItem, onChangeSchema, sortedSchema.streams]);

  return (
    <div>
      <SelectButton onClick={onCheckAll} type="button">
        {!!hasSelectedItem ? (
          <FormattedMessage id="sources.schemaUnselectAll" />
        ) : (
          <FormattedMessage id="sources.schemaSelectAll" />
        )}
      </SelectButton>
      {sortedSchema.streams.map(item => (
        <TreeViewRow item={item} updateItem={onUpdateItem} />
      ))}
    </div>
  );
};

export default TreeView;
