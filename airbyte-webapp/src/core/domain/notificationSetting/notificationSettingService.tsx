import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  getNotificationSetting,
  SaveNotificationUsageBody,
  saveNotificationUsageSetting,
  EditNotificationBody,
  editNotificationSetting,
  deleteNotificationSetting,
} from "../../request/DaspireClient";

export class NotificationService extends AirbyteRequestService {
  public get() {
    return getNotificationSetting(this.requestOptions);
  }

  public saveUsage(saveNotificationUsageBody: SaveNotificationUsageBody) {
    return saveNotificationUsageSetting(saveNotificationUsageBody, this.requestOptions);
  }

  public edit(editNotificationBody: EditNotificationBody) {
    return editNotificationSetting(editNotificationBody, this.requestOptions);
  }

  public delete(notificationSettingId: string) {
    return deleteNotificationSetting(notificationSettingId, this.requestOptions);
  }
}
