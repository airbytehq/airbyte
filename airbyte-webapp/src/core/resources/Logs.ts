import { ReadShape, Resource, SchemaDetail } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Logs {
  file?: Blob;
}

export default class LogsResource extends BaseResource implements Logs {
  readonly file?: Blob = undefined;

  pk(): string {
    return "";
  }

  static urlRoot = "logs";

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Logs>> {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<{ file: Blob }> => {
        const file = await this.fetchResponse(
          "post",
          `${this.url({})}/get`,
          params
        ).then((res) => res.blob());

        return { file };
      },
      schema: this,
    };
  }
}
