import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { deleteConnection, resetConnection, syncConnection } from "../../request/GeneratedApi";

export class ConnectionService extends AirbyteRequestService {
  public sync(connectionId: string) {
    return syncConnection({ connectionId }, this.requestOptions);
  }

  public reset(connectionId: string) {
    return resetConnection({ connectionId }, this.requestOptions);
  }

  public delete(connectionId: string) {
    return deleteConnection({ connectionId }, this.requestOptions);
  }
}
