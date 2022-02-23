import { MutateShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Notifications {
  status: string;
  message: string;
}

export default class NotificationsResource
  extends BaseResource
  implements Notifications {
  readonly status: string = "";
  readonly message: string = "";

  pk(): string {
    return "";
  }

  static urlRoot = "notifications";

  static tryShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<Notifications>> {
    return {
      ...super.partialUpdateShape(),
      getFetchKey: (params) =>
        "POST /notifications/try" + JSON.stringify(params),
      fetch: async (params) =>
        this.fetch("post", `${this.url(params)}/try`, params),
      schema: this,
    };
  }
}
