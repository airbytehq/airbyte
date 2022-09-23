import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, DropDownRow } from "components";
import { Popout } from "components/base/Popout/Popout";
import { Text } from "components/base/Text";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import styles from "./TableItemTitle.module.scss";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropDownData: DropDownRow.IDataItem[];
  onSelect: (item: DropDownRow.IDataItem) => void;
  entity: string;
  entityName: string;
  entityIcon?: React.ReactNode;
  releaseStage?: ReleaseStage;
}

const TableItemTitle: React.FC<TableItemTitleProps> = ({
  type,
  dropDownData,
  onSelect,
  entity,
  entityName,
  entityIcon,
  releaseStage,
}) => {
  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);
  const { formatMessage } = useIntl();
  const options = [
    {
      label: formatMessage({
        id: `tables.${type}AddNew`,
      }),
      value: "create-new-item",
      primary: true,
    },
    ...dropDownData,
  ];

  return (
    <>
      <div className={styles.entityInfo}>
        {entityIcon && <div className={styles.entityIcon}>{entityIcon}</div>}
        <div>
          <Text as="h2" size="md">
            {entityName}
          </Text>
          <Text as="p" size="lg" bold className={styles.entityType}>
            <span>{entity}</span>
            <ReleaseStageBadge stage={releaseStage} />
          </Text>
        </div>
      </div>
      <div className={styles.content}>
        <Text as="h3" size="sm">
          <FormattedMessage id="tables.connections" />
        </Text>
        <Popout
          data-testid={`select-${type}`}
          options={options}
          isSearchable={false}
          styles={{
            // TODO: hack to position select. Should be refactored with Headless UI Menu
            menuPortal: (base) => ({
              ...base,
              marginLeft: -130,
            }),
          }}
          menuShouldBlockScroll={false}
          onChange={onSelect}
          targetComponent={({ onOpen }) => (
            <Button onClick={onOpen} disabled={!allowCreateConnection}>
              <FormattedMessage id={`tables.${type}Add`} />
            </Button>
          )}
        />
      </div>
    </>
  );
};

export default TableItemTitle;
