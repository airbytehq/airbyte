import type { AnalyticsService } from "core/analytics/AnalyticsService";

export const useAnalyticsService = (): AnalyticsService => {
  return {
    page: jest.fn(),
    reset: jest.fn(),
    alias: jest.fn(),
    track: jest.fn(),
    identify: jest.fn(),
    group: jest.fn(),
    setContext: jest.fn(),
    removeFromContext: jest.fn(),
  } as unknown as AnalyticsService;
};
