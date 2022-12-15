import { ConnectionConfiguration } from "core/domain/connection";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { LogsRequestError } from "core/request/LogsRequestError";

import {
  CheckConnectionRead,
  CheckConnectionReadStatus,
  checkConnectionToDestination,
  checkConnectionToDestinationForUpdate,
  createDestination,
  deleteDestination,
  DestinationCoreConfig,
  DestinationCreate,
  DestinationUpdate,
  executeDestinationCheckConnection,
  getDestination,
  listDestinationsForWorkspace,
  updateDestination,
} from "../../request/AirbyteClient";

export class DestinationService extends AirbyteRequestService {
  public async check_connection(
    params: {
      destinationId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ) {
    let result: CheckConnectionRead;
    if (!params.destinationId) {
      result = await executeDestinationCheckConnection(params as DestinationCoreConfig, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else if (params.connectionConfiguration) {
      result = await checkConnectionToDestinationForUpdate(params as DestinationUpdate, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else {
      result = await checkConnectionToDestination(
        { destinationId: params.destinationId },
        {
          ...this.requestOptions,
          signal: requestParams?.signal,
        }
      );
    }

    if (result.status === CheckConnectionReadStatus.failed) {
      const jobInfo = {
        ...result.jobInfo,
        status: result.status,
      };

      throw new LogsRequestError(jobInfo, result.message);
    }

    return result;
  }

  public get(destinationId: string) {
    return getDestination({ destinationId }, this.requestOptions);
  }

  public list(workspaceId: string) {
    return listDestinationsForWorkspace({ workspaceId }, this.requestOptions);
  }

  public create(body: DestinationCreate) {
    return createDestination(body, this.requestOptions);
  }

  public update(body: DestinationUpdate) {
    return updateDestination(body, this.requestOptions);
  }

  public delete(destinationId: string) {
    return deleteDestination({ destinationId }, this.requestOptions);
  }
}
