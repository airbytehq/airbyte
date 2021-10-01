import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { User } from "./types";

class UserService extends AirbyteRequestService {
  get url(): string {
    return `users`;
  }

  public async getByEmail(email: string): Promise<User> {
    return this.fetch<User>(`${this.url}/get_by_email`, {
      email,
    });
  }

  public async getByAuthId(
    authUserId: string,
    authProvider: string
  ): Promise<User> {
    return this.fetch<User>(`${this.url}/get_by_auth_id`, {
      authUserId,
      authProvider,
    });
  }

  public async create(user: {
    authUserId: string;
    authProvider: string;
    email: string;
    name: string;
    invitedWorkspaceId?: string;
    status?: "invited";
  }): Promise<User> {
    return this.fetch<User>(`web_backend/users/create`, user);
  }

  public async remove(userId: string): Promise<void> {
    return this.fetch(`${this.url}/delete`, { userId });
  }

  public async invite(
    users: {
      email: string;
    }[],
    workspaceId: string
  ): Promise<User[]> {
    return Promise.all(
      users.map(async (user) =>
        this.fetch<User>(`web_backend/cloud_workspaces/invite`, {
          email: user.email,
          workspaceId,
        })
      )
    );
  }

  public async listByWorkspaceId(workspaceId: string): Promise<User[]> {
    const { users } = await this.fetch<{ users: User[] }>(
      `web_backend/permissions/list_users_by_workspace`,
      { workspaceId }
    );

    return users;
  }
}

export { UserService };
