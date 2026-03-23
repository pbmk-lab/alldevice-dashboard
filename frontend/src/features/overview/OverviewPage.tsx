import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState };

function toneForSeverity(severity: "critical" | "warning" | "info") {
  if (severity === "critical") return "alert-error";
  if (severity === "warning") return "alert-warning";
  return "alert-info";
}

export function OverviewPage() {
  const { locale, filters } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["overview", filters], queryFn: () => api.overview(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  const criticalAlerts = data.alerts.filter((item) => item.severity === "critical").length;
  const warningAlerts = data.alerts.filter((item) => item.severity === "warning").length;
  const qualityRate = Number(data.quality.missing_category_pct ?? 0);
  const anomalyCount = Number(data.quality.excluded_anomalies ?? 0);
  const topLines = data.downtime_by_line.slice(0, 5);
  const strongestType = data.downtime_by_type[0]?.name ?? "—";
  const strongestTypeShare = data.downtime_by_type[0]?.value ?? 0;

  let posture = tx(locale, "stable");
  let postureBadge = "badge-success";
  if (criticalAlerts > 0 || qualityRate > 30) {
    posture = tx(locale, "critical");
    postureBadge = "badge-error";
  } else if (warningAlerts > 0 || qualityRate > 10) {
    posture = tx(locale, "watch");
    postureBadge = "badge-warning";
  }

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "overview")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "overviewNote")}</h3>
            <div className="mt-5 flex flex-wrap gap-2">
              <div className={`badge badge-lg ${postureBadge}`}>{posture}</div>
              <div className="badge badge-outline badge-lg">
                {filters.lines.length} {tx(locale, "lines").toLowerCase()}
              </div>
              <div className="badge badge-outline badge-lg">
                {filters.dateStart} → {filters.dateEnd}
              </div>
            </div>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "currentPosture")}</div>
              <div className="stat-value text-2xl">{posture}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "quality")}</div>
              <div className="stat-value text-2xl">{qualityRate.toFixed(1)}%</div>
            </div>
            <div className="stat">
              <div className="stat-title">Anomalies</div>
              <div className="stat-value text-2xl">{anomalyCount}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        {data.kpis.map((kpi) => (
          <div key={kpi.id} className="stats border-base-300/70 bg-base-100 shadow-sm">
            <div className="stat">
              <div className="stat-title">{kpi.label}</div>
              <div className="stat-value text-4xl">
                {kpi.value}
                {kpi.unit ? ` ${kpi.unit}` : ""}
              </div>
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "priorityDesk")}
                </div>
                <h4 className="mt-2 text-2xl font-semibold">{data.top_line}</h4>
                <p className="text-base-content/80 mt-2 text-sm">
                  {tx(locale, "topDevice")}: <strong>{data.top_device}</strong>
                </p>
              </div>
              <div className="badge badge-outline badge-lg">
                {strongestType} · {strongestTypeShare.toFixed(1)}h
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "quality")}
                </div>
                <div className="mt-3 text-3xl font-semibold">{qualityRate.toFixed(1)}%</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "attentionQueue")}
                </div>
                <div className="mt-3 text-3xl font-semibold">{data.alerts.length}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">Anomalies</div>
                <div className="mt-3 text-3xl font-semibold">{anomalyCount}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "downtimeMix")}
                </div>
                <div className="mt-3 text-xl font-semibold">{strongestType}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-5">
          <div className="card border-base-300/70 bg-base-100 shadow-sm">
            <div className="card-body gap-4">
              <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                {tx(locale, "alerts")}
              </div>
              <div className="space-y-3">
                {data.alerts.length ? (
                  data.alerts.map((alert) => (
                    <div key={alert.id} className={`alert ${toneForSeverity(alert.severity)}`}>
                      <div>
                        <h4 className="font-semibold">{alert.title}</h4>
                        <p className="mt-1 text-sm">{alert.description}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="alert alert-success">
                    <span>{tx(locale, "noAlerts")}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="card border-base-300/70 bg-base-100 shadow-sm">
            <div className="card-body gap-4">
              <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                {tx(locale, "recommendations")}
              </div>
              <div className="space-y-3">
                {data.recommendations.length ? (
                  data.recommendations.map((item) => (
                    <div key={item.id} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                      <h4 className="font-semibold">{item.title}</h4>
                      <p className="text-base-content/80 mt-2 text-sm">{item.description}</p>
                    </div>
                  ))
                ) : (
                  <div className="alert alert-info">
                    <span>{tx(locale, "noRecommendations")}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title="MTTR"
          series={{
            x: data.mttr_trend.map((item) => item.period),
            y: data.mttr_trend.map((item) => item.value),
            name: "MTTR",
            color: "#11b1c9",
          }}
        />
        <ChartPanel
          title="MTBF"
          series={{
            x: data.mtbf_trend.map((item) => item.period),
            y: data.mtbf_trend.map((item) => item.value),
            name: "MTBF",
            color: "#ff9f1a",
          }}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "linePressure")}
            </div>
            <div className="space-y-3">
              {topLines.map((item, index) => {
                const maxValue = topLines[0]?.value || 1;
                return (
                  <div key={item.name} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="badge badge-primary badge-outline">{index + 1}</span>
                        <strong>{item.name}</strong>
                      </div>
                      <span className="text-sm font-semibold">{item.value.toFixed(1)}h</span>
                    </div>
                    <progress className="progress progress-primary h-2 w-full" value={item.value} max={maxValue} />
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="card from-neutral to-neutral/95 text-neutral-content bg-gradient-to-br shadow-sm">
          <div className="card-body gap-4">
            <div className="text-neutral-content/65 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "evidenceBoard")}
            </div>
            <div className="space-y-3">
              {data.downtime_by_type.map((item) => (
                <div key={item.name} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/6 px-4 py-3">
                  <span>{item.name}</span>
                  <strong>{item.value.toFixed(1)}h</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
