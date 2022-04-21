import Status from "core/statuses";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { checkOperation, OperationRead } from "../../request/GeneratedApi";

export class OperationService extends AirbyteRequestService {
  public async check({ operatorConfiguration }: OperationRead) {
    const rs = await checkOperation(operatorConfiguration, this.requestOptions);

    if (rs.status === Status.FAILED) {
      // TODO: place proper error
      throw new Error("failed");
    }

    return rs;
  }
}
