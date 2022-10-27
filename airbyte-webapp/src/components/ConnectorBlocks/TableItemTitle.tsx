import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { Button } from "components/ui/Button";
import { DropDownOptionDataItem } from "components/ui/DropDown";
import { Heading } from "components/ui/Heading";
import { Popout } from "components/ui/Popout";
import { Text } from "components/ui/Text";

import { ReleaseStage } from "core/request/AirbyteClient";

import styles from "./TableItemTitle.module.scss";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropDownData: DropDownOptionDataItem[];
  onSelect: (item: DropDownOptionDataItem) => void;
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
          <Heading as="h2">{entityName}</Heading>
          <Text size="lg" bold className={styles.entityType}>
            <span>{entity}</span>
            <ReleaseStageBadge stage={releaseStage} />
          </Text>
        </div>
      </div>
      <div className={styles.content}>
        <Heading as="h3" size="sm">
          <FormattedMessage id="tables.connections" />
        </Heading>
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
            <Button onClick={onOpen}>
              <FormattedMessage id={`tables.${type}Add`} />
            </Button>
          )}
        />
      </div>
    </>
  );
};

export default TableItemTitle;
