import { MutateShape, ReadShape, Resource, SchemaDetail } from "rest-hooks";
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

export default class WorkspaceResource
  extends BaseResource
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

  pk(): string {
    return this.workspaceId?.toString();
  }

  static urlRoot = "workspaces";

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Workspace[]>> {
    return {
      ...super.listShape(),
      schema: { workspaces: [this] },
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Workspace>> {
    return {
      ...super.detailShape(),
      schema: this,
    };
  }

  static updateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Workspace>> {
    return {
      ...super.partialUpdateShape(),
      schema: this,
    };
  }
}
