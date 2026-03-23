import { useQuery } from "@tanstack/react-query";
import { useOutletContext, useSearchParams } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState; availableLines: string[] };

export function DevicesPage() {
  const { locale, filters, availableLines } = useOutletContext<Context>();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedLine = searchParams.get("device_line") ?? "";
  const query = useQuery({
    queryKey: ["devices", filters, selectedLine],
    queryFn: () => api.devices(filters, selectedLine || undefined),
  });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data?.top_devices.length) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  const focusDevice = data.top_devices[0];
  const maxDowntime = data.top_devices[0]?.downtime_hours || 1;

  const setLineFocus = (value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set("device_line", value);
    else next.delete("device_line");
    setSearchParams(next, { replace: true });
  };

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "devices")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "devicesNote")}</h3>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "selectedLine")}</div>
              <div className="stat-value text-2xl">{selectedLine || tx(locale, "allLines")}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "reportsCount")}</div>
              <div className="stat-value text-2xl">{data.top_devices.length}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "topCause")}</div>
              <div className="stat-value text-xl">{data.category_breakdown[0]?.name ?? "—"}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "lineFocus")}
          </div>
          <select className="select select-bordered w-full max-w-md" value={selectedLine} onChange={(event) => setLineFocus(event.target.value)}>
            <option value="">{tx(locale, "allLines")}</option>
            {availableLines.map((line) => (
              <option key={line} value={line}>
                {line}
              </option>
            ))}
          </select>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "focusDevice")}
                </div>
                <h4 className="mt-2 text-2xl font-semibold">{focusDevice.device_name}</h4>
                <p className="text-base-content/80 mt-2 text-sm">
                  {tx(locale, "topLine")}: <strong>{focusDevice.line}</strong>
                </p>
              </div>
              <div className="badge badge-outline badge-lg">{focusDevice.downtime_hours.toFixed(1)}h</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "reportsCount")}</div>
                <div className="mt-3 text-3xl font-semibold">{focusDevice.events}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">Avg event</div>
                <div className="mt-3 text-3xl font-semibold">{focusDevice.avg_event_hours.toFixed(1)}h</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "topCause")}</div>
                <div className="mt-3 text-xl font-semibold">{data.category_breakdown[0]?.name ?? "—"}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "causeContribution")}</div>
                <div className="mt-3 text-xl font-semibold">{(data.category_breakdown[0]?.value ?? 0).toFixed(1)}h</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "deviceRanking")}
            </div>
            <div className="space-y-3">
              {data.top_devices.map((row, index) => (
                <div key={`${row.device_name}-${row.line}`} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <div>
                        <strong>{row.device_name}</strong>
                        <div className="text-base-content/76 text-xs">{row.line}</div>
                      </div>
                    </div>
                    <span className="text-sm font-semibold">{row.downtime_hours.toFixed(1)}h</span>
                  </div>
                  <progress className="progress progress-primary h-2 w-full" value={row.downtime_hours} max={maxDowntime} />
                  <div className="text-base-content/78 mt-3 flex flex-wrap gap-3 text-sm">
                    <span>{row.events} events</span>
                    <span>{row.avg_event_hours.toFixed(1)}h avg</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "topDeviceTrend")}
          series={{
            x: data.monthly_top_device_trend.map((item) => item.period),
            y: data.monthly_top_device_trend.map((item) => item.value),
            name: "Downtime",
            color: "#11b1c9",
          }}
        />
        <ChartPanel
          title={tx(locale, "causeContribution")}
          type="bar"
          series={{
            x: data.category_breakdown.map((item) => item.name),
            y: data.category_breakdown.map((item) => item.value),
            name: "Hours",
            color: "#ff9f1a",
          }}
        />
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "deviceLoad")}
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Line</th>
                  <th>Downtime h</th>
                  <th>Events</th>
                  <th>Avg h</th>
                </tr>
              </thead>
              <tbody>
                {data.top_devices.map((row) => (
                  <tr key={`${row.device_name}-${row.line}`}>
                    <td>{row.device_name}</td>
                    <td>{row.line}</td>
                    <td>{row.downtime_hours.toFixed(1)}</td>
                    <td>{row.events}</td>
                    <td>{row.avg_event_hours.toFixed(1)}</td>
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
