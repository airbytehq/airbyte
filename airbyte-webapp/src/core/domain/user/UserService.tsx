import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  addUsers,
  listUser,
  deleteUser,
  resendInviteToUser,
  updateUserRole,
  updateUserLang,
  registerNewUser,
} from "../../request/DaspireClient";
import { UpdateRoleRequestBody } from "../role";
import { NewUser, NewUserRegisterBody } from "./User";

export class UserService extends AirbyteRequestService {
  public list() {
    return listUser(this.requestOptions);
  }

  public add(users: NewUser[]) {
    return addUsers(users, this.requestOptions);
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

  public updateLang(lang: string) {
    return updateUserLang(lang, this.requestOptions);
  }

  public registerUser(newUserRegisterBody: NewUserRegisterBody) {
    return registerNewUser(newUserRegisterBody, this.requestOptions);
  }
}
