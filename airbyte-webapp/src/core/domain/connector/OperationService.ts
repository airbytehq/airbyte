import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Operation } from "./operation";

class OperationService extends AirbyteRequestService {
  get url() {
    return "operations";
  }

  public async check(
    body: Operation
  ): Promise<{ status: "succeeded" | "failed"; message: string }> {
    return (await this.fetch(`${this.url}/check`, body)) as any;
  }
}

export const operationService = new OperationService();
