import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { DropdownMenu } from "components/ui/DropdownMenu";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReleaseStage } from "core/request/AirbyteClient";

import { DropdownMenuItemType } from "../ui/DropdownMenu/DropdownMenu";
import styles from "./TableItemTitle.module.scss";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropDownData: DropdownMenuItemType[];
  onSelect: (item: DropdownMenuItemType) => void;
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
        <DropdownMenu
          label={<FormattedMessage id={`tables.${type}Add`} />}
          options={options}
          onChange={onSelect}
          disabled={!allowCreateConnection}
        />
      </div>
    </>
  );
};

export default TableItemTitle;
