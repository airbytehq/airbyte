import { useMutation } from "react-query";

import { useConfig } from "config";
import { GetLogsPayload, LogsService } from "core/domain/logs/LogsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

export const logsKeys = {
  all: ["logs"] as const,
  details: () => [...logsKeys.all, "detail"] as const,
  detail: (id: number | string) => [...logsKeys.details(), id] as const,
};

function useGetLogsService(): LogsService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new LogsService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

export function useGetLogs() {
  const service = useGetLogsService();

  return useMutation((payload: GetLogsPayload) => service.get(payload)).mutateAsync;
}
