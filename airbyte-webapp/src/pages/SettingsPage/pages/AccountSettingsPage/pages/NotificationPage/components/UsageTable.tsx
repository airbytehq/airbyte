import React from "react";
import { FormattedMessage } from "react-intl";

import { Row, Cell } from "components";
import { Separator } from "components/Separator";

import { EditNotificationBody, NotificationItem } from "core/request/DaspireClient";

import { FirstHeaderText, HeaderText, FirstCellFlexValue, BodyCell } from "./StyledTable";
import { UsageTableRow } from "./UsageTableRow";

interface IProps {
  usageList: NotificationItem[];
  createNotificationSetting: () => void;
  updateNotificationSetting: (data: EditNotificationBody) => void;
  deleteNotificationSetting: (notificationSettingId: string) => void;
}

export const UsageTable: React.FC<IProps> = ({
  usageList,
  createNotificationSetting,
  updateNotificationSetting,
  deleteNotificationSetting,
}) => {
  return (
    <>
      {/* Table Header Row */}
      <Row>
        <Cell flex={FirstCellFlexValue}>
          <FirstHeaderText>
            <FormattedMessage id="usageTable.cell.usage" />
          </FirstHeaderText>
        </Cell>
        <BodyCell>
          <HeaderText>
            <FormattedMessage id="usageTable.cell.email" />
          </HeaderText>
        </BodyCell>
        <BodyCell>
          <HeaderText>
            <FormattedMessage id="usageTable.cell.inApp" />
          </HeaderText>
        </BodyCell>
      </Row>
      {/* Table Body Rows */}
      {usageList
        .slice(0)
        .reverse()
        .map((usageItem) => (
          <>
            <Separator />
            <UsageTableRow
              usageItem={usageItem}
              createNotificationSetting={createNotificationSetting}
              updateNotificationSetting={updateNotificationSetting}
              deleteNotificationSetting={deleteNotificationSetting}
            />
          </>
        ))}
    </>
  );
};
