import Status from "core/statuses";

import { checkOperation, OperationRead } from "../../request/GeneratedApi";

export class OperationService {
  public async check({ operatorConfiguration }: OperationRead) {
    const rs = await checkOperation(operatorConfiguration);

    if (rs.status === Status.FAILED) {
      // TODO: place proper error
      throw new Error("failed");
    }

    return rs;
  }
}
