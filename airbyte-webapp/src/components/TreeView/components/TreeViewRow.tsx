import React, { useCallback, useMemo, useState } from "react";

import { Cell } from "../../SimpleTableComponents";
import MainInfoCell from "./MainInfoCell";
import SyncSettingsCell from "./SyncSettingsCell";
import ChildRow from "./ChildRow";

import {
  SyncSchemaStream,
  SyncSchemaField
} from "../../../core/resources/Schema";
import ItemRow from "./ItemRow";
import TreeItem from "./TreeItem";

type IProps = {
  isChild?: boolean;
  item: SyncSchemaStream;
  updateItem: (a: any) => void;
};

const TreeViewRow: React.FC<IProps> = ({ item, updateItem }) => {
  const [expanded, setExpanded] = useState<Array<string>>([]);
  const isItemOpen = useMemo(
    () => !!expanded.find(expandedItem => expandedItem === item.name),
    [expanded, item.name]
  );

  const onExpand = useCallback(() => {
    if (isItemOpen) {
      const newState = expanded.filter(stateItem => stateItem !== item.name);
      setExpanded(newState);
    } else {
      setExpanded([...expanded, item.name]);
    }
  }, [expanded, isItemOpen, item.name]);

  const isItemHasChildren = !!(item.fields && item.fields.length);

  const onSelectSyncMode = useCallback(
    (mode: string) => {
      return updateItem({ ...item, syncMode: mode });
    },
    [item, updateItem]
  );

  const isItemSelected = useCallback(() => {
    if (!isItemHasChildren) {
      return !!item.selected;
    }

    return !item.fields.find(field => !field.selected);
  }, [isItemHasChildren, item.fields, item.selected]);

  const onUpdateField = useCallback(
    (field: SyncSchemaField) => {
      const updatedFields = item.fields.map(itemField => {
        if (field.name === itemField.name) {
          return field;
        }

        return itemField;
      });

      updateItem({ ...item, fields: updatedFields });
    },
    [item, updateItem]
  );

  const onCheckBoxClick = useCallback(() => {
    if (!isItemHasChildren) {
      return updateItem({ ...item, selected: !item.selected });
    }
    const isFullySelected = !item.fields.find(field => !field.selected);
    const newFields = item.fields.map(field => {
      return isFullySelected
        ? { ...field, selected: false }
        : { ...field, selected: true };
    });

    return updateItem({ ...item, fields: newFields });
  }, [isItemHasChildren, item, updateItem]);

  return (
    <>
      <TreeItem>
        <ItemRow>
          <MainInfoCell
            label={item.name}
            onCheckBoxClick={onCheckBoxClick}
            onExpand={onExpand}
            isItemChecked={!!isItemSelected()}
            isItemHasChildren={isItemHasChildren}
            isItemOpen={isItemOpen}
          />
          <Cell />
          <Cell>{item.cleanedName}</Cell>
          <SyncSettingsCell
            item={item as SyncSchemaStream}
            onSelect={onSelectSyncMode}
          />
        </ItemRow>
      </TreeItem>
      {isItemOpen &&
        isItemHasChildren &&
        item.fields?.map(field => (
          <ChildRow item={field} isChild updateItem={onUpdateField} />
        ))}
    </>
  );
};

export default TreeViewRow;
