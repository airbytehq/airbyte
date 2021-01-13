import { Resource } from "rest-hooks";
import BaseResource from "./BaseResource";

export interface Deployment {
  status?: string;
  file?: any;
}

export default class DeploymentResource extends BaseResource
  implements Deployment {
  readonly status?: string = "";
  readonly file: any | undefined = undefined;

  pk() {
    return undefined;
  }

  static urlRoot = "deployment";

  static exportShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const file = await this.fetchResponse(
          "post",
          `${this.url(params)}/export`,
          params
        )
          .then(res => res.blob())
          .then(blob => {
            return window.URL.createObjectURL(blob);
          });

        return {
          file
        };
      },
      schema: {}
    };
  }
}
