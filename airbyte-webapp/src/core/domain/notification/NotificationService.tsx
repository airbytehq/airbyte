import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { Notification, tryNotificationConfig } from "../../request/GeneratedApi";

export class NotificationService extends AirbyteRequestService {
  public try(notification: Notification) {
    return tryNotificationConfig(notification, this.requestOptions);
  }
}
