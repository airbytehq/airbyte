import { useCallback, useEffect, useState } from "react";
import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { SyncSchema } from "core/domain/catalog";
import { Connection, ConnectionConfiguration } from "core/domain/connection";
import { Source } from "core/domain/connector";
import { SourceService } from "core/domain/connector/SourceService";
import { JobInfo } from "core/domain/job";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { isDefined } from "utils/common";

import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";
import { SCOPE_WORKSPACE } from "../../services/Scope";
import { connectionsKeys, ListConnection } from "./useConnectionHook";
import { useCurrentWorkspace } from "./useWorkspace";

export const sourcesKeys = {
  all: [SCOPE_WORKSPACE, "sources"] as const,
  lists: () => [...sourcesKeys.all, "list"] as const,
  list: (filters: string) => [...sourcesKeys.lists(), { filters }] as const,
  detail: (sourceId: string) => [...sourcesKeys.all, "details", sourceId] as const,
};

type ValuesProps = {
  name: string;
  serviceType?: string;
  connectionConfiguration?: ConnectionConfiguration;
  frequency?: string;
};

type ConnectorProps = { name: string; sourceDefinitionId: string };

function useSourceService(): SourceService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new SourceService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

type SourceList = { sources: Source[] };

const useSourceList = (): SourceList => {
  const workspace = useCurrentWorkspace();
  const service = useSourceService();

  return useSuspenseQuery(sourcesKeys.lists(), () => service.list(workspace.workspaceId));
};

const useGetSource = <T extends string | undefined | null>(
  sourceId: T
): T extends string ? Source : Source | undefined => {
  const service = useSourceService();

  return useSuspenseQuery(sourcesKeys.detail(sourceId ?? ""), () => service.get(sourceId ?? ""), {
    enabled: isDefined(sourceId),
  });
};

const useCreateSource = () => {
  const service = useSourceService();
  const queryClient = useQueryClient();
  const workspace = useCurrentWorkspace();

  const analyticsService = useAnalyticsService();

  return useMutation(
    async (createSourcePayload: { values: ValuesProps; sourceConnector?: ConnectorProps }) => {
      const { values, sourceConnector } = createSourcePayload;
      analyticsService.track("New Source - Action", {
        action: "Test a connector",
        connector_source: sourceConnector?.name,
        connector_source_id: sourceConnector?.sourceDefinitionId,
      });

      try {
        // Try to crete source
        const result = await service.create({
          name: values.name,
          sourceDefinitionId: sourceConnector?.sourceDefinitionId,
          workspaceId: workspace.workspaceId,
          connectionConfiguration: values.connectionConfiguration,
        });

        analyticsService.track("New Source - Action", {
          action: "Tested connector - success",
          connector_source: sourceConnector?.name,
          connector_source_id: sourceConnector?.sourceDefinitionId,
        });

        return result;
      } catch (e) {
        analyticsService.track("New Source - Action", {
          action: "Tested connector - failure",
          connector_source: sourceConnector?.name,
          connector_source_id: sourceConnector?.sourceDefinitionId,
        });
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

  return useMutation(
    (payload: { source: Source; connectionsWithSource: Connection[] }) => service.delete(payload.source.sourceId),
    {
      onSuccess: (_data, ctx) => {
        analyticsService.track("Source - Action", {
          action: "Delete source",
          connector_source: ctx.source.sourceName,
          connector_source_id: ctx.source.sourceDefinitionId,
        });

        queryClient.removeQueries(sourcesKeys.detail(ctx.source.sourceId));
        queryClient.setQueryData(
          sourcesKeys.lists(),
          (lst: SourceList | undefined) =>
            ({
              sources: lst?.sources.filter((conn) => conn.sourceId !== ctx.source.sourceId) ?? [],
            } as SourceList)
        );

        // To delete connections with current source from local store
        const connectionIds = ctx.connectionsWithSource.map((item) => item.connectionId);

        queryClient.setQueryData(connectionsKeys.lists(), (ls: ListConnection | undefined) => ({
          connections: ls?.connections.filter((c) => connectionIds.includes(c.connectionId)) ?? [],
        }));
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

const useDiscoverSchema = (
  sourceId?: string
): {
  isLoading: boolean;
  schema: SyncSchema;
  schemaErrorStatus: { status: number; response: JobInfo } | null;
  catalogId: string;
  onDiscoverSchema: () => Promise<void>;
} => {
  const service = useSourceService();
  const [schema, setSchema] = useState<SyncSchema>({ streams: [] });
  const [catalogId, setCatalogId] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [schemaErrorStatus, setSchemaErrorStatus] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const onDiscoverSchema = useCallback(async () => {
    setIsLoading(true);
    setSchemaErrorStatus(null);
    try {
      const data = await service.discoverSchema(sourceId || "");
      setSchema(data.catalog);
      setCatalogId(data.catalogId);
    } catch (e) {
      setSchemaErrorStatus(e);
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceId]);

  useEffect(() => {
    (async () => {
      if (sourceId) {
        await onDiscoverSchema();
      }
    })();
  }, [onDiscoverSchema, sourceId]);

  return { schemaErrorStatus, isLoading, schema, catalogId, onDiscoverSchema };
};

export { useSourceList, useGetSource, useCreateSource, useDeleteSource, useUpdateSource, useDiscoverSchema };
