import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Workspace {
  workspaceId: string;
  customerId: string;
  name: string;
  slug: string;
  initialSetupComplete: boolean;
  anonymousDataCollection: boolean;
  news: boolean;
  securityUpdates: boolean;
  displaySetupWizard: boolean;
}

export default class WorkspaceResource extends BaseResource
  implements Workspace {
  readonly workspaceId: string = "";
  readonly customerId: string = "";
  readonly name: string = "";
  readonly slug: string = "";
  readonly initialSetupComplete: boolean = false;
  readonly anonymousDataCollection: boolean = false;
  readonly news: boolean = false;
  readonly securityUpdates: boolean = false;
  readonly displaySetupWizard: boolean = true;

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
