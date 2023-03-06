import React from "react";
import styled from "styled-components";

import { Separator } from "components/Separator";

import { useNotificationSetting } from "services/notificationSetting/NotificationSettingService";

import { SyncTable } from "./components/SyncTable";
import { UsageTable } from "./components/UsageTable";

const PageContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 30px 16px;
`;

const NotificationPage: React.FC = () => {
  const { usageList, syncFail, syncSuccess } = useNotificationSetting();

  return (
    <PageContainer>
      <UsageTable usageList={usageList} />
      <Separator height="30px" />
      <SyncTable syncFail={syncFail} syncSuccess={syncSuccess} />
    </PageContainer>
  );
};

export default NotificationPage;
