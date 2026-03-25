import { useQuery } from "@tanstack/react-query";
import { useOutletContext, useSearchParams } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState; themeMode: "light" | "dark" };

export function TechniciansPage() {
  const { locale, filters, themeMode } = useOutletContext<Context>();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedTechnician = searchParams.get("technician_focus") ?? "";
  const query = useQuery({
    queryKey: ["technicians", filters, selectedTechnician],
    queryFn: () => api.technicians(filters, selectedTechnician || undefined),
  });

  const setTechnicianFocus = (value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set("technician_focus", value);
    else next.delete("technician_focus");
    setSearchParams(next, { replace: true });
  };

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  if (!data.technician_hours.length) {
    return <PageState kind="empty" message={tx(locale, "empty")} />;
  }

  const focusName = data.selected_technician ?? data.technician_hours[0]?.name ?? "";
  const selectedReportMetric = data.technician_reports.find((item) => item.name === focusName);
  const leadService = data.service_breakdown[0];
  const leadDevice = data.device_breakdown[0];
  const leadLine = data.line_breakdown[0];
  const maxHours = data.technician_hours[0]?.value || 1;

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-3xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "technicians")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "techniciansNote")}</h3>
            <p className="text-base-content/78 mt-3 text-sm">{tx(locale, "techniciansAllocationHint")}</p>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "selectedTechnician")}</div>
              <div className="stat-value text-xl">{focusName || "—"}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "reportsCount")}</div>
              <div className="stat-value text-2xl">{selectedReportMetric?.value ?? 0}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "topService")}</div>
              <div className="stat-value text-xl">{leadService?.name ?? "—"}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "selectedTechnician")}
          </div>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <select className="select select-bordered w-full max-w-lg" value={focusName} onChange={(event) => setTechnicianFocus(event.target.value)}>
              {data.technician_hours.map((item) => (
                <option key={item.name} value={item.name}>
                  {item.name}
                </option>
              ))}
            </select>

            <button type="button" className="btn btn-outline" onClick={() => setTechnicianFocus("")}>
              {tx(locale, "resetTechnicianFocus")}
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        {data.kpis.map((kpi) => (
          <div key={kpi.id} className="stats border-base-300/70 bg-base-100 shadow-sm">
            <div className="stat">
              <div className="stat-title">
                {kpi.id === "technicians"
                  ? tx(locale, "techniciansCount")
                  : kpi.id === "avg_hours"
                    ? tx(locale, "avgPerTechnician")
                    : kpi.label}
              </div>
              <div className="stat-value text-4xl">
                {kpi.value}
                {kpi.unit ? ` ${kpi.unit}` : ""}
              </div>
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "technicianRanking")}
            </div>
            <div className="space-y-3">
              {data.technician_hours.map((item, index) => (
                <button
                  key={item.name}
                  type="button"
                  className={[
                    "w-full rounded-2xl border p-4 text-left transition-colors",
                    item.name === focusName
                      ? "border-primary/40 bg-primary/10"
                      : "border-base-300/80 bg-base-200/55 hover:bg-base-200/80",
                  ].join(" ")}
                  onClick={() => setTechnicianFocus(item.name)}
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <strong>{item.name}</strong>
                    </div>
                    <span className="text-sm font-semibold">{item.value.toFixed(1)}h</span>
                  </div>
                  <progress className="progress progress-primary h-2 w-full" value={item.value} max={maxHours} />
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div>
              <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                {tx(locale, "technicianFocus")}
              </div>
              <h4 className="mt-2 text-2xl font-semibold">{focusName}</h4>
              <p className="text-base-content/80 mt-2 text-sm">
                {tx(locale, "topService")}: <strong>{leadService?.name ?? "—"}</strong>
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "reportsCount")}</div>
                <div className="mt-3 text-3xl font-semibold">{selectedReportMetric?.value ?? 0}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "allocatedHours")}</div>
                <div className="mt-3 text-3xl font-semibold">
                  {data.technician_hours.find((item) => item.name === focusName)?.value.toFixed(1) ?? "0.0"}h
                </div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "topDevice")}</div>
                <div className="mt-3 text-xl font-semibold">{leadDevice?.name ?? "—"}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "selectedLine")}</div>
                <div className="mt-3 text-xl font-semibold">{leadLine?.name ?? "—"}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "technicianServices")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.service_breakdown.map((item) => item.name),
            y: data.service_breakdown.map((item) => item.value),
            name: "Hours",
            color: "#11b1c9",
          }}
        />
        <ChartPanel
          title={tx(locale, "technicianDevices")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.device_breakdown.map((item) => item.name),
            y: data.device_breakdown.map((item) => item.value),
            name: "Hours",
            color: "#ff9f1a",
          }}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <ChartPanel
          title={tx(locale, "technicianLines")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.line_breakdown.map((item) => item.name),
            y: data.line_breakdown.map((item) => item.value),
            name: "Hours",
            color: "#0f766e",
          }}
        />

        <div className="card from-neutral to-neutral/95 text-neutral-content bg-gradient-to-br shadow-sm">
          <div className="card-body gap-4">
            <div className="text-neutral-content/65 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "technicianReports")}
            </div>
            <div className="space-y-3">
              {data.rows.slice(0, 8).map((row, index) => (
                <div key={`${row.report_nr}-${index}`} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/6 px-4 py-3">
                  <div>
                    <div className="font-medium">{row.service_name}</div>
                    <div className="text-neutral-content/70 text-xs">
                      {row.device_name} · {row.line}
                    </div>
                  </div>
                  <strong>{row.allocated_hours.toFixed(1)}h</strong>
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
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>{tx(locale, "selectedTechnician")}</th>
                  <th>Report</th>
                  <th>Service</th>
                  <th>Device</th>
                  <th>{tx(locale, "selectedLine")}</th>
                  <th>{tx(locale, "allocatedHours")}</th>
                  <th>{tx(locale, "sourceHours")}</th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row, index) => (
                  <tr key={`${row.report_nr}-${index}`}>
                    <td>{row.technician_name}</td>
                    <td>{row.report_nr}</td>
                    <td>{row.service_name}</td>
                    <td>{row.device_name}</td>
                    <td>{row.line}</td>
                    <td>{row.allocated_hours.toFixed(1)}</td>
                    <td>{row.source_total_hours.toFixed(1)}</td>
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
