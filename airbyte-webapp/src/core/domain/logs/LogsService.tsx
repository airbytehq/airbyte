import { getLogs, LogsRequestBody } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { LogType } from "./types";

export interface GetLogsPayload {
  logType: LogType;
}

export class LogsService extends AirbyteRequestService {
  public get(payload: LogsRequestBody) {
    return getLogs(payload, this.requestOptions);
  }
}
