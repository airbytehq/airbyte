import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { getLogs, LogsRequestBody } from "../../request/GeneratedApi";
import { LogType } from "./types";

export type GetLogsPayload = { logType: LogType };

export class LogsService extends AirbyteRequestService {
  public get(payload: LogsRequestBody) {
    return getLogs(payload, this.requestOptions);
  }
}
