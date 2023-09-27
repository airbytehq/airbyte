import React, { useEffect, useState } from "react";
import styled from "styled-components";

import { Separator } from "components/Separator";

import { EditNotificationRead, NotificationItem } from "core/request/DaspireClient";
import { useAppNotification } from "hooks/services/AppNotification";
import { useAsyncActions, useNotificationSetting } from "services/notificationSetting/NotificationSettingService";

import { PaymentTable } from "./components/PaymentTable";
import { SyncTable } from "./components/SyncTable";
import { UsageTable } from "./components/UsageTable";

export interface LoadingNotificationItem extends NotificationItem {
  isLoading: boolean;
}

const PageContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 30px 70px;
`;

export const CharacterInID = "__";

const NotificationPage: React.FC = () => {
  const { setNotification } = useAppNotification();
  const { usageList, syncFail, syncSuccess, paymentFail } = useNotificationSetting();

  const [usageNotificationList, setUsageNotificationList] = useState<NotificationItem[]>([]);
  const newUsageItem: NotificationItem = {
    id: `${Math.random() * 1000 * Math.random()}${CharacterInID}`,
    type: "USAGE",
    value: 0.3,
    emailFlag: true,
    appsFlag: true,
  };

  useEffect(() => setUsageNotificationList(usageList), [usageList]);

  const { onCreateNotificationSetting, onUpdateNotificationSetting, onDeleteNotificationSetting } = useAsyncActions();

  const createNotificationSetting = () => setUsageNotificationList((prev) => [newUsageItem, ...prev]);

  const saveNotificationSetting = (data: NotificationItem) => {
    onCreateNotificationSetting(data).catch((err: Error) => {
      setNotification({ message: err.message, type: "error" });
    });
  };

  const [updateLoading, setUpdateLoading] = useState<boolean>(false);
  const updateNotificationSetting = (data: NotificationItem) => {
    if (data.id.includes(CharacterInID)) {
      setUsageNotificationList((prev) => {
        const usageList = [...prev];
        const index = usageList.findIndex((item) => item.id === data.id);
        if (index >= 0) {
          usageList[index] = data;
        }
        return usageList;
      });
    } else {
      setUpdateLoading(true);
      onUpdateNotificationSetting(data)
        .then((res: EditNotificationRead) => {
          const { data } = res;
          if (data.type === "USAGE") {
            const myUsageNotificationList = [...usageNotificationList];
            const index = myUsageNotificationList.findIndex((item) => item.id === data.id);
            if (index >= 0) {
              myUsageNotificationList[index] = data;
            }
            setUsageNotificationList(myUsageNotificationList);
          }
          setUpdateLoading(false);
        })
        .catch((err: Error) => {
          setNotification({ message: err.message, type: "error" });
          setUpdateLoading(false);
        });
    }
  };

  const deleteNotificationSetting = (id: string) => {
    if (id.includes(CharacterInID)) {
      setUsageNotificationList((prev) => prev.filter((usageItem) => usageItem.id !== id));
    } else {
      onDeleteNotificationSetting(id).catch((err: Error) => {
        setNotification({ message: err.message, type: "error" });
      });
    }
  };

  return (
    <PageContainer>
      <UsageTable
        usageList={usageList}
        usageNotificationList={usageNotificationList}
        createNotificationSetting={createNotificationSetting}
        saveNotificationSetting={saveNotificationSetting}
        updateLoading={updateLoading}
        updateNotificationSetting={updateNotificationSetting}
        deleteNotificationSetting={deleteNotificationSetting}
      />
      <Separator height="30px" />
      <SyncTable
        syncFail={syncFail}
        syncSuccess={syncSuccess}
        updateLoading={updateLoading}
        updateNotificationSetting={updateNotificationSetting}
      />
      <Separator height="30px" />
      <PaymentTable paymentFail={paymentFail} />
    </PageContainer>
  );
};

export default NotificationPage;
