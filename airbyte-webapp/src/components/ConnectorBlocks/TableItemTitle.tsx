import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { DropdownMenu, DropdownMenuOptionType } from "components/ui/DropdownMenu";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReleaseStage } from "core/request/AirbyteClient";

import { Button } from "../ui/Button";
import styles from "./TableItemTitle.module.scss";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropdownOptions: DropdownMenuOptionType[];
  onSelect: (data: DropdownMenuOptionType) => void;
  entity: string;
  entityName: string;
  entityIcon?: React.ReactNode;
  releaseStage?: ReleaseStage;
}

const TableItemTitle: React.FC<TableItemTitleProps> = ({
  type,
  dropdownOptions,
  onSelect,
  entity,
  entityName,
  entityIcon,
  releaseStage,
}) => {
  const { formatMessage } = useIntl();

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
          placement="bottom-end"
          options={[
            {
              as: "button",
              className: styles.primary,
              displayName: formatMessage({
                id: `tables.${type}AddNew`,
              }),
            },
            ...dropdownOptions,
          ]}
          onChange={onSelect}
        >
          {() => (
            <Button data-id={`select-${type}`}>
              <FormattedMessage id={`tables.${type}Add`} />
            </Button>
          )}
        </DropdownMenu>
      </div>
    </>
  );
};

export default TableItemTitle;
