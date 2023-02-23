import { useCallback, useEffect, useState } from "react";
import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { Action, Namespace } from "core/analytics";
import { SyncSchema } from "core/domain/catalog";
import { ConnectionConfiguration } from "core/domain/connection";
import { SourceService } from "core/domain/connector/SourceService";
import { JobInfo } from "core/domain/job";
import { useInitService } from "services/useInitService";
import { isDefined } from "utils/common";

import { useAnalyticsService } from "./Analytics";
import { useRemoveConnectionsFromList } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";
import { SourceRead, WebBackendConnectionListItem } from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";

export const sourcesKeys = {
  all: [SCOPE_WORKSPACE, "sources"] as const,
  lists: () => [...sourcesKeys.all, "list"] as const,
  list: (filters: string) => [...sourcesKeys.lists(), { filters }] as const,
  detail: (sourceId: string) => [...sourcesKeys.all, "details", sourceId] as const,
};

interface ValuesProps {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
  frequency?: string;
}

interface ConnectorProps {
  name: string;
  sourceDefinitionId: string;
}

function useSourceService() {
  const { apiUrl } = useConfig();
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  return useInitService(() => new SourceService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

interface SourceList {
  sources: SourceRead[];
}

const useSourceList = (): SourceList => {
  const workspace = useCurrentWorkspace();
  const service = useSourceService();

  return useSuspenseQuery(sourcesKeys.lists(), () => service.list(workspace.workspaceId));
};

const useGetSource = <T extends string | undefined | null>(
  sourceId: T
): T extends string ? SourceRead : SourceRead | undefined => {
  const service = useSourceService();

  return useSuspenseQuery(sourcesKeys.detail(sourceId ?? ""), () => service.get(sourceId ?? ""), {
    enabled: isDefined(sourceId),
  });
};

export const useInvalidateSource = <T extends string | undefined | null>(sourceId: T): (() => void) => {
  const queryClient = useQueryClient();

  return useCallback(() => {
    queryClient.invalidateQueries(sourcesKeys.detail(sourceId ?? ""));
  }, [queryClient, sourceId]);
};

const useCreateSource = () => {
  const service = useSourceService();
  const queryClient = useQueryClient();
  const workspace = useCurrentWorkspace();

  return useMutation(
    async (createSourcePayload: { values: ValuesProps; sourceConnector: ConnectorProps }) => {
      const { values, sourceConnector } = createSourcePayload;
      try {
        // Try to create source
        const result = await service.create({
          name: values.name,
          sourceDefinitionId: sourceConnector?.sourceDefinitionId,
          workspaceId: workspace.workspaceId,
          connectionConfiguration: values.connectionConfiguration,
        });

        return result;
      } catch (e) {
        throw e;
      }
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(sourcesKeys.lists(), (lst: SourceList | undefined) => ({
          sources: [data, ...(lst?.sources ?? [])],
        }));
      },
    }
  );
};

const useDeleteSource = () => {
  const service = useSourceService();
  const queryClient = useQueryClient();
  const analyticsService = useAnalyticsService();
  const removeConnectionsFromList = useRemoveConnectionsFromList();

  return useMutation(
    (payload: { source: SourceRead; connectionsWithSource: WebBackendConnectionListItem[] }) =>
      service.delete(payload.source.sourceId),
    {
      onSuccess: (_data, ctx) => {
        analyticsService.track(Namespace.SOURCE, Action.DELETE, {
          actionDescription: "Source deleted",
          connector_source: ctx.source.sourceName,
          connector_source_definition_id: ctx.source.sourceDefinitionId,
        });

        queryClient.removeQueries(sourcesKeys.detail(ctx.source.sourceId));
        queryClient.setQueryData(
          sourcesKeys.lists(),
          (lst: SourceList | undefined) =>
            ({
              sources: lst?.sources.filter((conn) => conn.sourceId !== ctx.source.sourceId) ?? [],
            } as SourceList)
        );

        const connectionIds = ctx.connectionsWithSource.map((item) => item.connectionId);
        removeConnectionsFromList(connectionIds);
      },
    }
  );
};

const useUpdateSource = () => {
  const service = useSourceService();
  const queryClient = useQueryClient();

  return useMutation(
    (updateSourcePayload: { values: ValuesProps; sourceId: string }) => {
      return service.update({
        name: updateSourcePayload.values.name,
        sourceId: updateSourcePayload.sourceId,
        connectionConfiguration: updateSourcePayload.values.connectionConfiguration,
      });
    },
    {
      onSuccess: (data) => {
        queryClient.setQueryData(sourcesKeys.detail(data.sourceId), data);
      },
    }
  );
};

export type SchemaError = (Error & { status: number; response: JobInfo }) | null;

const useDiscoverSchema = (
  sourceId: string,
  disableCache?: boolean
): {
  isLoading: boolean;
  schema: SyncSchema;
  schemaErrorStatus: SchemaError;
  catalogId: string | undefined;
  onDiscoverSchema: () => Promise<void>;
} => {
  const service = useSourceService();
  const [schema, setSchema] = useState<SyncSchema>({ streams: [] });
  const [catalogId, setCatalogId] = useState<string | undefined>("");
  const [isLoading, setIsLoading] = useState(false);
  const [schemaErrorStatus, setSchemaErrorStatus] = useState<SchemaError>(null);

  const onDiscoverSchema = useCallback(async () => {
    setIsLoading(true);
    setSchemaErrorStatus(null);
    try {
      const data = await service.discoverSchema(sourceId || "", disableCache);
      setSchema(data.catalog);
      setCatalogId(data.catalogId);
    } catch (e) {
      setSchemaErrorStatus(e);
    } finally {
      setIsLoading(false);
    }
  }, [disableCache, service, sourceId]);

  useEffect(() => {
    if (sourceId) {
      onDiscoverSchema();
    }
  }, [onDiscoverSchema, sourceId]);

  return { schemaErrorStatus, isLoading, schema, catalogId, onDiscoverSchema };
};

export { useSourceList, useGetSource, useCreateSource, useDeleteSource, useUpdateSource, useDiscoverSchema };
