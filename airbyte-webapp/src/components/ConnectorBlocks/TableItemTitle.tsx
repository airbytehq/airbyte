import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { DropdownMenu } from "components/ui/DropdownMenu";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReleaseStage } from "core/request/AirbyteClient";

import { Button } from "../ui/Button";
import { DropdownMenuItemType, IconPositionType } from "../ui/DropdownMenu/DropdownMenu";
import styles from "./TableItemTitle.module.scss";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropDownData: any[];
  onSelect: (item: any) => void;
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
  // const options = [
  //   {
  //     label: formatMessage({
  //       id: `tables.${type}AddNew`,
  //     }),
  //     value: "create-new-item",
  //     primary: true,
  //   },
  //   ...dropDownData,
  // ];
  // onChange={onSelect}

  // type: DropdownMenuItemType.BUTTON;
  // icon: React.ReactNode;
  // displayName: React.ReactNode;
  // iconPosition?: IconPositionType;
  // primary?: boolean;
  // onClick?: () => void;
  console.log(onSelect);
  console.log(dropDownData);
  // const options = [
  //   {
  //     type: DropdownMenuItemType.BUTTON,
  //     icon: <span>Hi</span>,
  //     iconPosition: IconPositionType.RIGHT,
  //     primary: true,
  //     displayName: formatMessage({
  //       id: `tables.${type}AddNew`,
  //     }),
  //   },
  // ];
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
              type: DropdownMenuItemType.BUTTON,
              primary: true,
              displayName: formatMessage({
                id: `tables.${type}AddNew`,
              }),
            },
            ...dropDownData.map(
              (item) =>
                ({
                  type: DropdownMenuItemType.BUTTON,
                  icon: item.img,
                  iconPosition: IconPositionType.RIGHT,
                  displayName: item.label,
                  onSelect,
                } as any)
            ),
          ]}
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
