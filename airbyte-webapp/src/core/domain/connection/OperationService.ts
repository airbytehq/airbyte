import { checkOperation, CheckOperationReadStatus, OperationCreate } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class OperationService extends AirbyteRequestService {
  public async check({ operatorConfiguration }: OperationCreate) {
    const rs = await checkOperation(operatorConfiguration, this.requestOptions);

    if (rs.status === CheckOperationReadStatus.failed) {
      // TODO: place proper error
      throw new Error("failed");
    }

    return rs;
  }
}
