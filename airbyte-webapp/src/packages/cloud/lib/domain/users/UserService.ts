import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { User } from "./types";

class UserService extends AirbyteRequestService {
  get url() {
    return `users`;
  }

  public async getByEmail(email: string): Promise<User> {
    const rs = ((await this.fetch(`${this.url}/get_by_email`, {
      email,
    })) as any) as User;

    return rs;
  }

  public async getByAuthId(
    authUserId: string,
    authProvider: string
  ): Promise<User> {
    const rs = ((await this.fetch(`${this.url}/get_by_auth_id`, {
      authUserId,
      authProvider,
    })) as any) as User;

    return rs;
  }

  public async create(user: {
    authUserId: string;
    authProvider: string;
    email: string;
    name: string;
  }): Promise<User> {
    const rs = ((await this.fetch(
      `web_backend/users/create`,
      user
    )) as any) as User;

    return rs;
  }

  public async listByWorkspaceId(workspaceId: string): Promise<User[]> {
    return (
      await this.fetch<{ users: User[] }>(
        `web_backend/permissions/list_users_by_workspace`,
        { workspaceId }
      )
    ).users;
  }
}

export { UserService };
