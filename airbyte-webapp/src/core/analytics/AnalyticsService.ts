import config from "config";
import { SegmentAnalytics } from "./types";

export class AnalyticsService {
  private static getAnalytics = (): SegmentAnalytics | undefined =>
    window.analytics;

  static alias = (newId: string): void =>
    AnalyticsService.getAnalytics()?.alias?.(newId);

  static page = (name: string): void =>
    AnalyticsService.getAnalytics()?.page?.(name);

  static reset = (): void => AnalyticsService.getAnalytics()?.reset?.();

  static track = (name: string, properties: Record<string, unknown>): void =>
    AnalyticsService.getAnalytics()?.track?.(name, {
      user_id: config.ui.workspaceId,
      ...properties,
      airbyte_version: config.version,
    });

  static identify = (
    userId: string,
    traits: Record<string, unknown> = {}
  ): void => AnalyticsService.getAnalytics()?.identify?.(userId, traits);

  static group = (
    organisationId: string,
    traits: Record<string, unknown> = {}
  ): void => AnalyticsService.getAnalytics()?.group?.(organisationId, traits);
}
