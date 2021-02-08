import { Resource } from "rest-hooks";
import BaseResource, { NetworkError } from "./BaseResource";

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
      fetch: async (): Promise<any> => {
        const file = await this.fetchResponse(
          "post",
          `${this.url({})}/export`,
          {}
        )
          .then(res => res.blob())
          .then(blob => {
            return window.URL.createObjectURL(blob);
          });

        return {
          file
        };
      },
      schema: { file: "" }
    };
  }

  static importShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      fetch: async (
        _: Readonly<Record<string, string | number>>,
        file: string
      ): Promise<any> => {
        let options: RequestInit = {
          method: "POST",
          headers: {
            "Content-Type": "application/x-gzip",
            "Content-Encoding": "gzip"
          },
          body: file
        };
        const response = fetch(`${this.url({})}/import`, options).then(
          result => {
            if (result.status >= 200 && result.status < 300) {
              return result;
            } else {
              const e = new NetworkError(result);
              e.status = result.status;
              throw e;
            }
          }
        );
        return response;
      },
      schema: null
    };
  }
}
