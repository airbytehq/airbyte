import { Notification, tryNotificationConfig } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class NotificationService extends AirbyteRequestService {
  public try(notification: Notification) {
    return tryNotificationConfig(notification, this.requestOptions);
  }
}
