import {
  deleteConnection,
  resetConnection,
  syncConnection,
  getState,
  setState,
  ConnectionState,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

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

  public getState(connectionId: string) {
    return getState({ connectionId }, this.requestOptions);
  }

  public setState(connectionId: string, state: ConnectionState) {
    return setState({ connectionId, state }, this.requestOptions);
  }
}
