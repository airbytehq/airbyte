interface SegmentAnalytics {
  page: (name?: string) => void;
  reset: () => void;
  alias: (newId: string) => void;
  track: (name: string, properties: Record<string, unknown>) => void;
  identify: (userId?: string, traits?: Record<string, unknown>) => void;
  group: (organisationId: string, traits: Record<string, unknown>) => void;
}

export type { SegmentAnalytics };
