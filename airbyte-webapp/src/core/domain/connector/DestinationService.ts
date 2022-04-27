import { ConnectionConfiguration } from "core/domain/connection";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
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
    if (!params.destinationId) {
      return executeDestinationCheckConnection(params as DestinationCoreConfig, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else if (params.connectionConfiguration) {
      return checkConnectionToDestinationForUpdate(params as DestinationUpdate, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else {
      return checkConnectionToDestination(
        { destinationId: params.destinationId },
        {
          ...this.requestOptions,
          signal: requestParams?.signal,
        }
      );
    }
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
