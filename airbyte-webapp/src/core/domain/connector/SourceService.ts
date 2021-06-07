import { AirbyteRequestService } from "core/request/AirbyteRequestService";
// import { Schema } from "core/resources/Schema";
import config from "config";
// import { toInnerModel } from "../catalog";

class SourceService extends AirbyteRequestService {
  constructor(private rootUrl: string) {
    super();
  }

  get url() {
    return this.rootUrl + "sources";
  }

  // public async discoverSchema(params: { sourceId: string }): Promise<Schema> {
  //   const response = await SourceService.fetch(
  //     `${this.url}/discover_schema`,
  //     params
  //   );
  //
  //   const result = toInnerModel(response);
  //
  //   return {
  //     catalog: result.catalog,
  //     jobInfo: result.jobInfo,
  //     id: params.sourceId,
  //   };
  // }
}

export const sourceService = new SourceService(config.apiUrl);
