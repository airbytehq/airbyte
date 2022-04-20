import { getLogs, LogsRequestBody } from "../../request/GeneratedApi";
import { LogType } from "./types";

export type GetLogsPayload = { logType: LogType };

export class LogsService {
  public get({ logType }: LogsRequestBody) {
    return getLogs({ logType });
  }
}
