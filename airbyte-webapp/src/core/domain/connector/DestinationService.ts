import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import Status from "core/statuses";
import { LogsRequestError } from "core/request/LogsRequestError";
import { Scheduler } from "./types";
import { ConnectionConfiguration } from "core/domain/connection";

class DestinationService extends AirbyteRequestService {
  get url(): string {
    return "destinations";
  }

  public async check_connection(
    params: {
      destinationId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ): Promise<Scheduler> {
    const url = !params.destinationId
      ? `scheduler/${this.url}/check_connection`
      : params.connectionConfiguration
      ? `${this.url}/check_connection_for_update`
      : `${this.url}/check_connection`;

    // migrated from rest-hooks. Needs proper fix to `Scheduler` type
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(url, params, requestParams);

    // If check connection for destination has status 'failed'
    if (result.status === Status.FAILED) {
      const jobInfo = {
        ...result.jobInfo,
        status: result.status,
      };

      throw new LogsRequestError(jobInfo, jobInfo, result.message);
    }

    return result;
  }
}

export { DestinationService };
