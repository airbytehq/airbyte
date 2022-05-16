import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { NotificationStatus } from "./types";

class NotificationService extends AirbyteRequestService {
  get url(): string {
    return "notifications";
  }

  public try(payload: {
    notificationType: "slack";
    sendOnSuccess: boolean;
    sendOnFailure: boolean;
    slackConfiguration: {
      webhook: string;
    };
  }): Promise<NotificationStatus> {
    return this.fetch<NotificationStatus>(`${this.url}/try`, payload);
  }
}

export { NotificationService };
