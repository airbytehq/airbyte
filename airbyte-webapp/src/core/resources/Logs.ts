import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Logs {
  file?: any;
}

export default class LogsResource extends BaseResource implements Logs {
  readonly file: any | undefined = undefined;

  pk() {
    return undefined;
  }

  static urlRoot = "logs";

  static detailShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const file = await this.fetchResponse(
          "post",
          `${this.url({})}/get`,
          params
        ).then(res => res.blob());

        return { file };
      },
      schema: this.asSchema()
    };
  }
}
