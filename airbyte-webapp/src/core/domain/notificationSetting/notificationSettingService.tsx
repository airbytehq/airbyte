import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  getNotificationSetting,
  SaveNotificationUsageBody,
  createNotificationUsageSetting,
  EditNotificationBody,
  NotificationItem,
  editNotificationSetting,
  deleteNotificationSetting,
  ignoreNotification,
} from "../../request/DaspireClient";

export class NotificationService extends AirbyteRequestService {
  public get() {
    return getNotificationSetting(this.requestOptions);
  }

  public createUsage(notificationUsage: SaveNotificationUsageBody) {
    return createNotificationUsageSetting(notificationUsage, this.requestOptions);
  }

  public edit(data: NotificationItem) {
    if (data.type === "USAGE") {
      return editNotificationSetting(data, this.requestOptions);
    }
    const syncNotificationEditBody: EditNotificationBody = {
      id: data.id,
      emailFlag: data.emailFlag,
      appsFlag: data.appsFlag,
    };
    return editNotificationSetting(syncNotificationEditBody, this.requestOptions);
  }

  public delete(notificationSettingId: string) {
    return deleteNotificationSetting(notificationSettingId, this.requestOptions);
  }

  public ignore() {
    return ignoreNotification(this.requestOptions);
  }
}
