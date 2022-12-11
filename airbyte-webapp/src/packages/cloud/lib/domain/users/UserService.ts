import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { User, UserUpdate } from "./types";

export class UserService extends AirbyteRequestService {
  get url(): string {
    return "v1/users";
  }

  public async getByEmail(email: string): Promise<User> {
    return this.fetch<User>(`${this.url}/get_by_email`, {
      email,
    });
  }

  public async getByAuthId(authUserId: string, authProvider: string): Promise<User> {
    return this.fetch<User>(`${this.url}/get_by_auth_id`, {
      authUserId,
      authProvider,
    });
  }

  public async update(params: UserUpdate): Promise<void> {
    return this.fetch<void>(`${this.url}/update`, params);
  }

  public async changeName(authUserId: string, userId: string, name: string): Promise<void> {
    return this.fetch<void>(`${this.url}/update`, {
      authUserId,
      userId,
      name,
    });
  }

  public async changeEmail(email: string): Promise<void> {
    return this.fetch<void>(`${this.url}/update`, {
      email,
    });
  }

  public async create(user: {
    authUserId: string;
    authProvider: string;
    email: string;
    name: string;
    companyName: string;
    news: boolean;
    invitedWorkspaceId?: string;
    status?: "invited";
  }): Promise<User> {
    return this.fetch<User>(`v1/web_backend/users/create`, user);
  }

  public async revokeUserSession(): Promise<void> {
    return this.fetch("v1/web_backend/users/revoke_user_session");
  }

  public async remove(workspaceId: string, email: string): Promise<void> {
    return this.fetch(`v1/web_backend/cloud_workspaces/revoke_user`, {
      email,
      workspaceId,
    });
  }

  public async resendWithSignInLink({ email }: { email: string }): Promise<void> {
    this.fetch(`v1/web_backend/cloud_workspaces/resend_with_signin_link`, {
      email,
      // `continueUrl` is rquired to have a valid URL, but it's currently not used by the Frontend.
      continueUrl: window.location.href,
    });
  }

  public async invite(
    users: Array<{
      email: string;
    }>,
    workspaceId: string
  ): Promise<User[]> {
    return Promise.all(
      users.map(async (user) =>
        this.fetch<User>(`v1/web_backend/cloud_workspaces/invite_with_signin_link`, {
          email: user.email,
          workspaceId,
          continueUrl: window.location.href,
        })
      )
    );
  }

  public async listByWorkspaceId(workspaceId: string): Promise<User[]> {
    const { users } = await this.fetch<{ users: User[] }>(`v1/web_backend/permissions/list_users_by_workspace`, {
      workspaceId,
    });

    return users;
  }
}
