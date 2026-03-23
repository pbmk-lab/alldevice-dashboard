import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState };

export function DataQualityPage() {
  const { locale, filters } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["data-quality", filters], queryFn: () => api.dataQuality(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  const qualityRows = [...data.quality_by_line].sort((a, b) => b.value - a.value);
  const focusLine = qualityRows[0];
  const maxMissing = qualityRows[0]?.value || 1;

  let posture = tx(locale, "operationallyReady");
  let postureBadge = "badge-success";
  if (data.missing_category_pct > 30 || data.excluded_anomalies > 0) {
    posture = tx(locale, "unavailable");
    postureBadge = "badge-error";
  } else if (data.missing_category_pct > 10) {
    posture = tx(locale, "degraded");
    postureBadge = "badge-warning";
  }

  const actionHint =
    data.missing_category_pct > 30
      ? locale === "lv"
        ? "Ieviest obligātu cēloņu norādi un operatīvu kontroli pa maiņām."
        : "Make cause capture mandatory and review it per shift."
      : data.excluded_anomalies > 0
        ? locale === "lv"
          ? "Pārskatīt anomālos ierakstus un korekti nodalīt ilgstošos gadījumus."
          : "Review anomalous records and separate long-running cases correctly."
        : locale === "lv"
          ? "Turpināt monitoringu un noturēt cēloņu kvalitāti virs pašreizējā līmeņa."
          : "Continue monitoring and keep cause quality above the current level.";

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "dataQuality")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "qualityNote")}</h3>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "qualityPosture")}</div>
              <div className="stat-value text-2xl">{posture}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "anomalyBurden")}</div>
              <div className="stat-value text-2xl">{data.excluded_anomalies}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "worstLine")}</div>
              <div className="stat-value text-xl">{focusLine?.name ?? "—"}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-3 md:grid-cols-2">
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">{tx(locale, "qualityDebt")}</div>
            <div className="stat-value text-4xl">{data.missing_category_pct.toFixed(1)}%</div>
          </div>
        </div>
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">{tx(locale, "anomalyBurden")}</div>
            <div className="stat-value text-4xl">{data.excluded_anomalies}</div>
          </div>
        </div>
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">{tx(locale, "anomalyHours")}</div>
            <div className="stat-value text-4xl">{data.excluded_anomaly_hours.toFixed(1)}h</div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "qualityFocus")}
                </div>
                <h4 className="mt-2 text-2xl font-semibold">{focusLine?.name ?? "—"}</h4>
              </div>
              <div className={`badge badge-lg ${postureBadge}`}>{posture}</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "qualityDebt")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.missing_category_pct.toFixed(1)}%</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "anomalyBurden")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.excluded_anomalies}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "anomalyHours")}</div>
                <div className="mt-3 text-2xl font-semibold">{data.excluded_anomaly_hours.toFixed(1)}h</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "activeLines")}</div>
                <div className="mt-3 text-3xl font-semibold">{qualityRows.length}</div>
              </div>
            </div>

            <div className="alert alert-warning">
              <span>{actionHint}</span>
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "qualityRanking")}
            </div>
            <div className="space-y-3">
              {qualityRows.map((item, index) => (
                <div key={item.name} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <strong>{item.name}</strong>
                    </div>
                    <span className="text-sm font-semibold">{item.value.toFixed(1)}%</span>
                  </div>
                  <progress className="progress progress-error h-2 w-full" value={item.value} max={maxMissing} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title="Missing cause by line"
          type="bar"
          series={{
            x: data.quality_by_line.map((item) => item.name),
            y: data.quality_by_line.map((item) => item.value),
            name: "Missing %",
            color: "#ef4444",
          }}
        />
        <ChartPanel
          title="Anomaly distribution"
          type="bar"
          series={{
            x: data.anomaly_distribution.map((item) => item.name),
            y: data.anomaly_distribution.map((item) => item.value),
            name: "Anomalies",
            color: "#f59e0b",
          }}
        />
      </section>
    </div>
  );
}
