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
  SourceCreate,
  SourceUpdate,
  updateSource,
} from "../../request/GeneratedApi";
import { ConnectionConfiguration } from "../connection";

export class SourceService {
  public async check_connection(
    params: {
      sourceId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    // @ts-expect-error This is unusable with the generated requests
    requestParams?: RequestInit
  ) {
    // TODO: Fix params logic
    if (!params.sourceId) {
      return executeSourceCheckConnection(params as any);
    } else if (params.connectionConfiguration) {
      return checkConnectionToSourceForUpdate(params as any);
    } else {
      return checkConnectionToSource({ sourceId: params.sourceId });
    }
  }

  public get(sourceId: string) {
    return getSource({ sourceId });
  }

  public list(workspaceId: string) {
    return listSourcesForWorkspace({ workspaceId });
  }

  public create(body: SourceCreate) {
    return createSource(body);
  }

  public update(body: SourceUpdate) {
    return updateSource(body);
  }

  public delete(sourceId: string) {
    return deleteSource({ sourceId });
  }

  public async discoverSchema(sourceId: string) {
    const result = await discoverSchemaForSource({ sourceId });

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
      id: sourceId,
    };
  }
}
