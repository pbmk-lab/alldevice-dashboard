import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState };

export function WorkReportsPage() {
  const { locale, filters } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["work-reports", filters], queryFn: () => api.workReports(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  const topTechnician = data.technician_hours[0];
  const topService = data.service_hours[0];
  const maxTechHours = data.technician_hours[0]?.value || 1;
  const rawRows = data.raw_rows.slice(0, 8);

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "workReports")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "workReportsNote")}</h3>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "topTechnician")}</div>
              <div className="stat-value text-xl">{topTechnician?.name ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "topService")}</div>
              <div className="stat-value text-xl">{topService?.name ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "reportsCount")}</div>
              <div className="stat-value text-2xl">{data.kpis.find((item) => item.id === "reports")?.value ?? 0}</div>
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
            <div>
              <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                {tx(locale, "laborDesk")}
              </div>
              <h4 className="mt-2 text-2xl font-semibold">{topTechnician?.name ?? "—"}</h4>
              <p className="text-base-content/80 mt-2 text-sm">
                {tx(locale, "topService")}: <strong>{topService?.name ?? "—"}</strong>
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "technicianHours")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.technician_hours.length}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "serviceHours")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.service_hours.length}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "lineHours")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.line_hours.length}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "reportsCount")}</div>
                <div className="mt-3 text-3xl font-semibold">{data.kpis.find((item) => item.id === "reports")?.value ?? 0}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "technicianHours")}
            </div>
            <div className="space-y-3">
              {data.technician_hours.map((item, index) => (
                <div key={item.name || index} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <strong>{item.name || "—"}</strong>
                    </div>
                    <span className="text-sm font-semibold">{item.value.toFixed(1)}h</span>
                  </div>
                  <progress className="progress progress-primary h-2 w-full" value={item.value} max={maxTechHours} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "technicianHours")}
          type="bar"
          series={{
            x: data.technician_hours.map((item) => item.name),
            y: data.technician_hours.map((item) => item.value),
            name: "Hours",
            color: "#11b1c9",
          }}
        />
        <ChartPanel
          title={tx(locale, "serviceHours")}
          type="bar"
          series={{
            x: data.service_hours.map((item) => item.name),
            y: data.service_hours.map((item) => item.value),
            name: "Hours",
            color: "#ff9f1a",
          }}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "lineHours")}
          type="bar"
          series={{
            x: data.line_hours.map((item) => item.name),
            y: data.line_hours.map((item) => item.value),
            name: "Hours",
            color: "#0f766e",
          }}
        />

        <div className="card from-neutral to-neutral/95 text-neutral-content bg-gradient-to-br shadow-sm">
          <div className="card-body gap-4">
            <div className="text-neutral-content/65 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "effortMix")}
            </div>
            <div className="space-y-3">
              {data.service_hours.slice(0, 8).map((item) => (
                <div key={item.name} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/6 px-4 py-3">
                  <span>{item.name}</span>
                  <strong>{item.value.toFixed(1)}h</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "reportsTable")}
          </div>
          {rawRows.length ? (
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Report</th>
                    <th>Service</th>
                    <th>Device</th>
                    <th>Line</th>
                    <th>Users</th>
                    <th>Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {rawRows.map((row, index) => (
                    <tr key={`${String(row.report_id ?? row.report_nr ?? index)}`}>
                      <td>{String(row.report_id ?? "—")}</td>
                      <td>{String(row.report_nr ?? "—")}</td>
                      <td>{String(row.service_name ?? "—")}</td>
                      <td>{String(row.device_name ?? "—")}</td>
                      <td>{String(row.report_line ?? "—")}</td>
                      <td>{String(row.user_name_list ?? "—")}</td>
                      <td>{Number(row.total_hours ?? 0).toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="alert alert-info">
              <span>{tx(locale, "noRawRows")}</span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
