import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { ConnectionConfiguration } from "../connection";
import { Scheduler } from "./types";
import Status from "core/statuses";
import { LogsRequestError } from "core/request/LogsRequestError";

class SourceService extends AirbyteRequestService {
  get url(): string {
    return "sources";
  }

  public async check_connection(
    params: {
      sourceId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ): Promise<Scheduler> {
    const url = !params.sourceId
      ? `scheduler/${this.url}/check_connection`
      : params.connectionConfiguration
      ? `${this.url}/check_connection_for_update`
      : `${this.url}/check_connection`;

    const result = await this.fetch<Scheduler>(url, params, requestParams);

    // If check connection for source has status 'failed'
    if (result.status === Status.FAILED) {
      const jobInfo: any = {
        ...result.jobInfo,
        status: result.status,
      };

      throw new LogsRequestError(jobInfo, jobInfo, result.message);
    }

    return result;
  }
}

export { SourceService };
