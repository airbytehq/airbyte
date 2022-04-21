import { ConnectionConfiguration } from "core/domain/connection";

import { AirbyteRequestService } from "../../request/AirbyteRequestService";
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
} from "../../request/GeneratedApi";

export class DestinationService extends AirbyteRequestService {
  public async check_connection(
    params: {
      destinationId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    // @ts-expect-error This is unusable with the generated requests
    requestParams?: RequestInit
  ) {
    // TODO: Fix params logic
    if (!params.destinationId) {
      return executeDestinationCheckConnection(params as DestinationCoreConfig, this.requestOptions);
    } else if (params.connectionConfiguration) {
      return checkConnectionToDestinationForUpdate(params as DestinationUpdate, this.requestOptions);
    } else {
      return checkConnectionToDestination({ destinationId: params.destinationId }, this.requestOptions);
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
