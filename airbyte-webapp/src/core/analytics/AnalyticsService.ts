import * as FullStory from "@fullstory/browser";

import config from "config";
import { SegmentAnalytics } from "./types";

export class AnalyticsService {
  private static getSegmentAnalytics = (): SegmentAnalytics | undefined =>
    window.analytics;

  static alias = (newId: string): void =>
    AnalyticsService.getSegmentAnalytics()?.alias?.(newId);

  static page = (name: string): void =>
    AnalyticsService.getSegmentAnalytics()?.page?.(name);

  static reset = (): void => AnalyticsService.getSegmentAnalytics()?.reset?.();

  static track = (name: string, properties: Record<string, unknown>): void =>
    AnalyticsService.getSegmentAnalytics()?.track?.(name, {
      user_id: config.ui.workspaceId,
      ...properties,
      airbyte_version: config.version,
      environment: config.version === "dev" ? "dev" : "prod",
    });

  static identify = (
    userId: string,
    traits: Record<string, unknown> = {}
  ): void => {
    AnalyticsService.getSegmentAnalytics()?.identify?.(userId, traits);
    FullStory.identify(userId);
  };

  static group = (
    organisationId: string,
    traits: Record<string, unknown> = {}
  ): void =>
    AnalyticsService.getSegmentAnalytics()?.group?.(organisationId, traits);
}
