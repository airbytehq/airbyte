import React from "react";
import { FormattedMessage } from "react-intl";

import { Row, Cell } from "components";
import { Separator } from "components/Separator";

import { NotificationItem } from "core/request/DaspireClient";

import { NotificationFlag } from "./NotificationFlag";
import { FirstHeaderText, HeaderText, BodyRow, FirstCellFlexValue, BodyCell } from "./StyledTable";

interface IProps {
  syncFail: NotificationItem;
  syncSuccess: NotificationItem;
}

export const SyncTable: React.FC<IProps> = ({ syncFail, syncSuccess }) => {
  return (
    <>
      {/* Table Header Row */}
      <Row>
        <Cell flex={FirstCellFlexValue}>
          <FirstHeaderText>
            <FormattedMessage id="syncTable.cell.status" />
          </FirstHeaderText>
        </Cell>
      </Row>
      <Separator />
      {/* Table Body Rows */}
      <BodyRow>
        <Cell flex={FirstCellFlexValue}>
          <HeaderText>
            <FormattedMessage id="syncTable.cell.fail" />
          </HeaderText>
        </Cell>
        <BodyCell>
          <NotificationFlag isActive={syncFail.emailFlag} />
        </BodyCell>
        <BodyCell>
          <NotificationFlag isActive={syncFail.appsFlag} />
        </BodyCell>
      </BodyRow>
      <BodyRow>
        <Cell flex={FirstCellFlexValue}>
          <HeaderText>
            <FormattedMessage id="syncTable.cell.success" />
          </HeaderText>
        </Cell>
        <BodyCell>
          <NotificationFlag isActive={syncSuccess.emailFlag} />
        </BodyCell>
        <BodyCell>
          <NotificationFlag isActive={syncSuccess.appsFlag} />
        </BodyCell>
      </BodyRow>
    </>
  );
};
