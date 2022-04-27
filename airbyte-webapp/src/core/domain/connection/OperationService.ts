import Status from "core/statuses";

import { checkOperation, OperationRead } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

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
