import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { CommonRequestError } from "core/request/CommonRequestError";

import {
  checkConnectionToSource,
  checkConnectionToSourceForUpdate,
  createSource,
  deleteSource,
  discoverSchemaForSource,
  executeSourceCheckConnection,
  getSource,
  listSourcesForWorkspace,
  SourceCoreConfig,
  SourceCreate,
  SourceUpdate,
  updateSource,
} from "../../request/AirbyteClient";
import { ConnectionConfiguration } from "../connection";

export class SourceService extends AirbyteRequestService {
  public async check_connection(
    params: {
      sourceId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ) {
    if (!params.sourceId) {
      return executeSourceCheckConnection(params as SourceCoreConfig, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else if (params.connectionConfiguration) {
      return checkConnectionToSourceForUpdate(params as SourceUpdate, {
        ...this.requestOptions,
        signal: requestParams?.signal,
      });
    } else {
      return checkConnectionToSource(
        { sourceId: params.sourceId },
        { ...this.requestOptions, signal: requestParams?.signal }
      );
    }
  }

  public get(sourceId: string) {
    return getSource({ sourceId }, this.requestOptions);
  }

  public list(workspaceId: string) {
    return listSourcesForWorkspace({ workspaceId }, this.requestOptions);
  }

  public create(body: SourceCreate) {
    return createSource(body, this.requestOptions);
  }

  public update(body: SourceUpdate) {
    return updateSource(body, this.requestOptions);
  }

  public delete(sourceId: string) {
    return deleteSource({ sourceId }, this.requestOptions);
  }

  public async discoverSchema(sourceId: string) {
    const result = await discoverSchemaForSource({ sourceId }, this.requestOptions);

    if (!result.jobInfo?.succeeded || !result.catalog) {
      // @ts-expect-error TODO: address this case
      const e = new CommonRequestError(result);
      // Generate error with failed status and received logs
      e._status = 400;
      // @ts-ignore address this case
      e.response = result.jobInfo;
      throw e;
    }

    return {
      catalog: result.catalog,
      jobInfo: result.jobInfo,
      catalogId: result.catalogId,
      id: sourceId,
    };
  }
}
