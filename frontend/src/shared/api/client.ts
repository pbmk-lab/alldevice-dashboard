import type { Locale } from "../i18n/translations";

export type NamedMetric = { name: string; value: number; meta?: Record<string, unknown> };
export type KpiMetric = { id: string; label: string; value: number; unit?: string | null; status?: string | null };
export type AlertItem = { id: string; severity: "critical" | "warning" | "info"; title: string; description: string };
export type RecommendationItem = { id: string; title: string; description: string };
export type TrendPoint = { period: string; value: number };
export type FiltersResponse = {
  lines: string[];
  min_date: string;
  max_date: string;
  default_start: string;
  default_end: string;
  default_locale: Locale;
};
export type OverviewResponse = {
  locale: Locale;
  kpis: KpiMetric[];
  alerts: AlertItem[];
  recommendations: RecommendationItem[];
  top_line: string;
  top_device: string;
  mttr_trend: TrendPoint[];
  mtbf_trend: TrendPoint[];
  downtime_by_line: NamedMetric[];
  downtime_by_type: NamedMetric[];
  quality: Record<string, number>;
};
export type TriageRow = {
  line: string;
  downtime_hours: number;
  events: number;
  avg_event_hours: number;
  missing_pct: number;
  anomaly_count: number;
  priority: string;
  risk_score: number;
  top_category: string;
};
export type DevicesResponse = {
  locale: Locale;
  selected_line?: string | null;
  top_devices: Array<{
    device_name: string;
    line: string;
    downtime_hours: number;
    events: number;
    avg_event_hours: number;
  }>;
  category_breakdown: NamedMetric[];
  monthly_top_device_trend: TrendPoint[];
};
export type WorkReportsResponse = {
  locale: Locale;
  kpis: KpiMetric[];
  technician_hours: NamedMetric[];
  service_hours: NamedMetric[];
  line_hours: NamedMetric[];
  raw_rows: Record<string, unknown>[];
};
export type DataQualityResponse = {
  locale: Locale;
  missing_category_pct: number;
  excluded_anomalies: number;
  excluded_anomaly_hours: number;
  quality_by_line: NamedMetric[];
  anomaly_distribution: NamedMetric[];
};
export type DebugResponse = {
  statuses: Array<{ endpoint: string; ok: boolean; row_count: number; details: string }>;
};

export type FiltersState = {
  locale: Locale;
  dateStart: string;
  dateEnd: string;
  lines: string[];
};

function toQuery(params: Record<string, string | string[] | undefined>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, item));
      return;
    }
    if (value) {
      search.set(key, value);
    }
  });
  return search.toString();
}

async function getJson<T>(path: string, filters?: Partial<FiltersState> & { line?: string }) {
  const query = filters
    ? toQuery({
        locale: filters.locale,
        date_start: filters.dateStart,
        date_end: filters.dateEnd,
        lines: filters.lines,
        line: filters.line,
      })
    : "";
  const response = await fetch(`/api/${path}${query ? `?${query}` : ""}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export const api = {
  filters: () => getJson<FiltersResponse>("filters"),
  overview: (filters: FiltersState) => getJson<OverviewResponse>("overview", filters),
  triage: (filters: FiltersState) => getJson<{ locale: Locale; rows: TriageRow[] }>("triage/lines", filters),
  devices: (filters: FiltersState, line?: string) =>
    getJson<DevicesResponse>("devices", { ...filters, line }),
  workReports: (filters: FiltersState) => getJson<WorkReportsResponse>("work-reports", filters),
  dataQuality: (filters: FiltersState) => getJson<DataQualityResponse>("data-quality", filters),
  debug: (filters: FiltersState) => getJson<DebugResponse>("debug/upstream", filters),
};
