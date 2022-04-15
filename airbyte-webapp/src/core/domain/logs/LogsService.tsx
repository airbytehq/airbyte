import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { Logs, LogType } from "./types";

export type GetLogsPayload = { logType: LogType };

class LogsService extends AirbyteRequestService {
  get url(): string {
    return "logs";
  }

  public get(payload: GetLogsPayload): Promise<Logs> {
    return this.fetch<Logs>(`${this.url}/get`, payload);
  }
}

export { LogsService };
