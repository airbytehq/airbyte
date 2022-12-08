import { getLogs, LogsRequestBody } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class LogsService extends AirbyteRequestService {
  public get(payload: LogsRequestBody) {
    return getLogs(payload, this.requestOptions);
  }
}
