import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState };

export function AdminDebugPage() {
  const { locale, filters } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["debug", filters], queryFn: () => api.debug(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const statuses = query.data.statuses;
  const healthyCount = statuses.filter((item) => item.ok).length;
  const failingCount = statuses.length - healthyCount;
  const totalRows = statuses.reduce((sum, item) => sum + item.row_count, 0);

  let posture = tx(locale, "operationallyReady");
  let postureBadge = "badge-success";
  if (failingCount === statuses.length) {
    posture = tx(locale, "unavailable");
    postureBadge = "badge-error";
  } else if (failingCount > 0) {
    posture = tx(locale, "degraded");
    postureBadge = "badge-warning";
  }

  const actionGuide =
    failingCount > 0
      ? locale === "lv"
        ? "Pārbaudīt upstream savienojumu, endpoint formātu un credentials injekciju."
        : "Check upstream connectivity, endpoint response shape, and credential injection."
      : locale === "lv"
        ? "Sistēma atbild korekti; turpināt periodisku uzraudzību."
        : "System responds correctly; continue periodic monitoring.";

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "admin")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "adminNote")}</h3>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "systemPosture")}</div>
              <div className="stat-value text-2xl">{posture}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "endpointHealth")}</div>
              <div className="stat-value text-2xl">
                {healthyCount}/{statuses.length}
              </div>
            </div>
            <div className="stat">
              <div className="stat-title">Rows observed</div>
              <div className="stat-value text-2xl">{totalRows}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-3 md:grid-cols-2">
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">{tx(locale, "okLabel")}</div>
            <div className="stat-value text-4xl">{healthyCount}</div>
          </div>
        </div>
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">{tx(locale, "failLabel")}</div>
            <div className="stat-value text-4xl">{failingCount}</div>
          </div>
        </div>
        <div className="stats border-base-300/70 bg-base-100 shadow-sm">
          <div className="stat">
            <div className="stat-title">Rows</div>
            <div className="stat-value text-4xl">{totalRows}</div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "diagnosticBoard")}
                </div>
                <h4 className="mt-2 text-2xl font-semibold">{tx(locale, "endpointHealth")}</h4>
              </div>
              <div className={`badge badge-lg ${postureBadge}`}>{posture}</div>
            </div>

            <div className={failingCount > 0 ? "alert alert-warning" : "alert alert-success"}>
              <span>{actionGuide}</span>
            </div>

            <div className="space-y-3">
              {statuses.map((status) => (
                <div key={status.endpoint} className={`alert ${status.ok ? "alert-success" : "alert-error"}`}>
                  <div>
                    <h4 className="font-semibold">{status.endpoint}</h4>
                    <p className="mt-1 text-sm">{status.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "endpointHealth")}
            </div>
            <div className="space-y-3">
              {statuses.map((status, index) => (
                <div key={status.endpoint} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <strong>{status.endpoint}</strong>
                    </div>
                    <span className={`badge ${status.ok ? "badge-success" : "badge-error"}`}>
                      {status.ok ? tx(locale, "okLabel") : tx(locale, "failLabel")}
                    </span>
                  </div>
                  <div className="text-base-content/78 flex flex-wrap gap-3 text-sm">
                    <span>{status.row_count} rows</span>
                    <span>{status.details}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "diagnosticBoard")}
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Endpoint</th>
                  <th>{tx(locale, "status")}</th>
                  <th>Rows</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {statuses.map((status) => (
                  <tr key={status.endpoint}>
                    <td>{status.endpoint}</td>
                    <td>{status.ok ? tx(locale, "okLabel") : tx(locale, "failLabel")}</td>
                    <td>{status.row_count}</td>
                    <td>{status.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
