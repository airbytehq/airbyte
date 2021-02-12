import {
  Method,
  MutateShape,
  Resource,
  AbstractInstanceType,
  ReadShape,
  schemas,
  SchemaDetail,
  SchemaList
} from "rest-hooks";

// import { authService } from "../auth/authService";
import config from "../../config";

export class NetworkError extends Error {
  status: number;
  response: Response;

  constructor(response: Response) {
    super(response.statusText);
    this.status = response.status;
    this.response = response;
  }
}

export default abstract class BaseResource extends Resource {
  /** Perform network request and resolve with HTTP Response */
  static async fetchResponse(
    _: Method,
    url: string,
    body?: Readonly<object | string>
  ) {
    let options: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    };
    if (this.fetchOptionsPlugin) options = this.fetchOptionsPlugin(options);
    if (body) options.body = JSON.stringify(body);

    return fetch(url, options);
  }

  /** Perform network request and resolve with json body */
  static async fetch(
    method: Method,
    url: string,
    body?: Readonly<object | string>
  ) {
    const response = await this.fetchResponse(method, url, body);

    if (response.status >= 200 && response.status < 300) {
      return response.status === 204 ? {} : await response.json();
    } else {
      const e = new NetworkError(response);
      e.status = response.status;
      throw e;
    }
  }

  static listUrl<T extends typeof Resource>(this: T): string {
    return `${config.apiUrl}${this.urlRoot}`;
  }

  static url<T extends typeof Resource>(this: T): string {
    return `${config.apiUrl}${this.urlRoot}`;
  }

  static rootUrl(): string {
    return config.apiUrl;
  }

  static listShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaList<AbstractInstanceType<T>>> {
    return {
      ...(super.listShape() as any),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/list" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${this.listUrl(params)}/list`,
          { ...params }
        );
        return response;
      }
    };
  }

  static detailShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<AbstractInstanceType<T>>> {
    return {
      ...(super.detailShape() as any),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/get" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${this.url(params)}/get`,
          params
        );
        return response;
      }
    };
  }

  static createShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<AbstractInstanceType<T>>> {
    return {
      ...(super.createShape() as any),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/create" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>,
        body: Readonly<object>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${this.listUrl(params)}/create`,
          body
        );
        return response;
      }
    };
  }

  static deleteShape<T extends typeof Resource>(
    this: T
  ): MutateShape<schemas.Delete<T>, Readonly<object>, unknown> {
    return {
      ...(super.deleteShape() as any),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/delete" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${this.url(params)}/delete`,
          params
        );
        return response;
      }
    };
  }

  static partialUpdateShape<T extends typeof Resource>(
    this: T
  ): MutateShape<SchemaDetail<AbstractInstanceType<T>>> {
    return {
      ...(super.partialUpdateShape() as any),
      getFetchKey: (params: any) =>
        "POST " + this.url(params) + "/partial-update" + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, string | number>>,
        body: Readonly<object>
      ): Promise<any> => {
        const response = await this.fetch(
          "post",
          `${this.url(params)}/update`,
          body
        );
        return response;
      }
    };
  }
}
