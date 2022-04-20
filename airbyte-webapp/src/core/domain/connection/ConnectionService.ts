import { deleteConnection, resetConnection, syncConnection } from "../../request/GeneratedApi";

export class ConnectionService {
  public sync(connectionId: string) {
    return syncConnection({ connectionId });
  }

  public reset(connectionId: string) {
    return resetConnection({ connectionId });
  }

  public delete(connectionId: string) {
    return deleteConnection({ connectionId });
  }
}
