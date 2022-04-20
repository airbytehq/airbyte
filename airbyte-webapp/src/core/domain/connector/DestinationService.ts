import { ConnectionConfiguration } from "core/domain/connection";

import {
  checkConnectionToDestination,
  checkConnectionToDestinationForUpdate,
  createDestination,
  deleteDestination,
  DestinationCreate,
  DestinationUpdate,
  executeDestinationCheckConnection,
  getDestination,
  listDestinationsForWorkspace,
  updateDestination,
} from "../../request/GeneratedApi";

export class DestinationService {
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
      return executeDestinationCheckConnection(params as any);
    } else if (params.connectionConfiguration) {
      return checkConnectionToDestinationForUpdate(params as any);
    } else {
      return checkConnectionToDestination({ destinationId: params.destinationId });
    }
  }

  public get(destinationId: string) {
    return getDestination({ destinationId });
  }

  public list(workspaceId: string) {
    return listDestinationsForWorkspace({ workspaceId });
  }

  public create(body: DestinationCreate) {
    return createDestination(body);
  }

  public update(body: DestinationUpdate) {
    return updateDestination(body);
  }

  public delete(destinationId: string) {
    return deleteDestination({ destinationId });
  }
}
