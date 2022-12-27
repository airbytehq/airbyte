import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { addUsers, listUser, deleteUser, resendInviteToUser, updateUserRole } from "../../request/DaspireClient";
import { UpdateRoleRequestBody } from "../role";

export class UserService extends AirbyteRequestService {
  public list() {
    return listUser(this.requestOptions);
  }

  public add() {
    return addUsers(this.requestOptions);
  }

  public delete(userId: string) {
    return deleteUser(userId, this.requestOptions);
  }

  public resendInvite(userId: string) {
    return resendInviteToUser(userId, this.requestOptions);
  }

  public updateRole(UpdateRoleBody: UpdateRoleRequestBody) {
    return updateUserRole(UpdateRoleBody, this.requestOptions);
  }
}
