import React, { useEffect, useState } from "react";
import styled from "styled-components";

import { Separator } from "components/Separator";

import { EditNotificationBody, NotificationItem } from "core/request/DaspireClient";
import { useNotificationSetting, useAsyncActions } from "services/notificationSetting/NotificationSettingService";

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

  const [usageNotificationList, setUsageNotificationList] = useState<NotificationItem[]>([]);
  const newUsageItem: NotificationItem = {
    id: `${Math.random() * 1000 * Math.random()}_`,
    type: "USAGE",
    value: 0.3,
    emailFlag: false,
    appsFlag: false,
  };

  useEffect(() => setUsageNotificationList(usageList), [usageList]);

  const {
    // onCreateNotificationSetting,
    onUpdateNotificationSetting,
    onDeleteNotificationSetting,
  } = useAsyncActions();

  const createNotificationSetting = () => setUsageNotificationList((prev) => [newUsageItem, ...prev]);
  const updateNotificationSetting = (data: EditNotificationBody) => {
    onUpdateNotificationSetting(data);
  };
  const deleteNotificationSetting = (id: string) => {
    if (id.includes("_")) {
      setUsageNotificationList((prev) => prev.filter((usageItem) => usageItem.id !== id));
    } else {
      onDeleteNotificationSetting(id);
    }
  };

  return (
    <PageContainer>
      <UsageTable
        usageList={usageNotificationList}
        createNotificationSetting={createNotificationSetting}
        updateNotificationSetting={updateNotificationSetting}
        deleteNotificationSetting={deleteNotificationSetting}
      />
      <Separator height="30px" />
      <SyncTable syncFail={syncFail} syncSuccess={syncSuccess} updateNotificationSetting={updateNotificationSetting} />
    </PageContainer>
  );
};

export default NotificationPage;
