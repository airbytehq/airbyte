import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Workspace {
  workspaceId: string;
  name: string;
  slug: string;
  initialSetupComplete: boolean;
}

export default class WorkspaceResource extends BaseResource
  implements Workspace {
  readonly workspaceId: string = "";
  readonly name: string = "";
  readonly slug: string = "";
  readonly initialSetupComplete: boolean = false;

  pk() {
    return this.workspaceId?.toString();
  }

  static urlRoot = "workspaces";

  static listShape<T extends typeof Resource>(this: T) {
    return {
      ...super.listShape(),
      schema: { workspaces: [this.asSchema()] }
    };
  }

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      schema: this.asSchema()
    };
  }

  static detailBySlugShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> =>
        this.fetch("post", `${this.url(params)}/get_by_slug`, params),
      schema: this.asSchema()
    };
  }

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this.asSchema()
    };
  }
}
