import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { listRoles } from "../../request/DaspireClient";

export class RoleService extends AirbyteRequestService {
  public list() {
    return listRoles(this.requestOptions);
  }
}
