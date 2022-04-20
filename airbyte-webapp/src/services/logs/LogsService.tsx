import { useMutation } from "react-query";

import { GetLogsPayload, LogsService } from "core/domain/logs/LogsService";
import { useInitService } from "services/useInitService";

export const logsKeys = {
  all: ["logs"] as const,
  details: () => [...logsKeys.all, "detail"] as const,
  detail: (id: number | string) => [...logsKeys.details(), id] as const,
};

function useGetLogsService(): LogsService {
  return useInitService(() => new LogsService(), []);
}

export function useGetLogs() {
  const service = useGetLogsService();

  return useMutation((payload: GetLogsPayload) => service.get(payload)).mutateAsync;
}
