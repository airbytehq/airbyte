import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Workspace {
  workspaceId: string;
  name: string;
  slug: string;
  initialSetupComplete: boolean;
  onboardingComplete: boolean;
  anonymousDataCollection: boolean;
  news: boolean;
  securityUpdates: boolean;
}

export default class WorkspaceResource extends BaseResource
  implements Workspace {
  readonly workspaceId: string = "";
  readonly name: string = "";
  readonly slug: string = "";
  readonly initialSetupComplete: boolean = false;
  readonly onboardingComplete: boolean = false;
  readonly anonymousDataCollection: boolean = false;
  readonly news: boolean = false;
  readonly securityUpdates: boolean = false;

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

  static updateShape<T extends typeof Resource>(this: T) {
    return {
      ...super.partialUpdateShape(),
      schema: this.asSchema()
    };
  }
}
