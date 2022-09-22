import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, DropDownRow, H3, H5 } from "components";
import { Popout } from "components/base/Popout/Popout";
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
        {entityIcon && <span className={styles.entityIcon}>{entityIcon}</span>}
        <div>
          <H3 bold>{entityName}</H3>
          <H5 className={styles.entityType}>
            <span>{entity}</span>
            <ReleaseStageBadge stage={releaseStage} />
          </H5>
        </div>
      </div>
      <div className={styles.content}>
        <H5>
          <FormattedMessage id="tables.connections" />
        </H5>
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
