import { useQuery } from "@tanstack/react-query";
import { Link, useOutletContext, useSearchParams } from "react-router-dom";

import { api, type FiltersState, type TriageRow } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState };

function buildActionPlan(locale: Locale, row: TriageRow) {
  const actions: string[] = [];

  if (row.missing_pct > 25) {
    actions.push(
      locale === "lv"
        ? "Padarīt cēloņa izvēli obligātu un pārbaudīt pēdējo maiņu ierakstus."
        : "Make cause selection mandatory and review the latest shift entries.",
    );
  }

  if (row.anomaly_count > 0) {
    actions.push(
      locale === "lv"
        ? "Atvērt anomālos ierakstus un pārskatīt ilguma robežas šai līnijai."
        : "Open anomalous records and review duration thresholds for this line.",
    );
  }

  if (row.avg_event_hours > 5) {
    actions.push(
      locale === "lv"
        ? "Nošķirt remonta cikla aizturi: diagnostika, detaļas vai resurss."
        : "Separate repair-cycle delay into diagnosis, parts, or staffing bottlenecks.",
    );
  }

  if (!actions.length) {
    actions.push(
      locale === "lv"
        ? "Turēt līniju iknedēļas novērošanā un pārskatīt pēc nākamās maiņas."
        : "Keep this line on weekly watch and reassess after the next shift.",
    );
  }

  return actions.slice(0, 3);
}

function priorityTone(priority: string) {
  const value = priority.toLowerCase();
  if (value.includes("high") || value.includes("aug")) return "badge-error";
  if (value.includes("medium") || value.includes("vid")) return "badge-warning";
  return "badge-info";
}

export function TriagePage() {
  const { locale, filters } = useOutletContext<Context>();
  const [searchParams, setSearchParams] = useSearchParams();
  const query = useQuery({ queryKey: ["triage", filters], queryFn: () => api.triage(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data?.rows.length) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const rows = query.data.rows;
  const focusedLineName = searchParams.get("line_focus");
  const focusLine = rows.find((row) => row.line === focusedLineName) ?? rows[0];
  const maxRisk = rows[0]?.risk_score || 1;
  const maxDowntime = Math.max(...rows.map((row) => row.downtime_hours), 1);
  const maxEvents = Math.max(...rows.map((row) => row.events), 1);
  const maxAvgHours = Math.max(...rows.map((row) => row.avg_event_hours), 1);
  const worstMissing = rows.reduce((current, row) => (row.missing_pct > current.missing_pct ? row : current), rows[0]);
  const highPriority = rows.filter((row) => priorityTone(row.priority) === "badge-error").length;
  const anomalyLines = rows.filter((row) => row.anomaly_count > 0).length;
  const avgRisk = rows.reduce((sum, row) => sum + row.risk_score, 0) / rows.length;
  const playbook = buildActionPlan(locale, focusLine);

  const setFocusLine = (line: string) => {
    const next = new URLSearchParams(searchParams);
    next.set("line_focus", line);
    setSearchParams(next, { replace: true });
  };

  const devicesSearch = new URLSearchParams(searchParams);
  devicesSearch.set("device_line", focusLine.line);

  const driverItems = [
    {
      key: "downtime",
      label: tx(locale, "downtimeHours"),
      value: `${focusLine.downtime_hours.toFixed(1)}h`,
      score: focusLine.downtime_hours,
      max: maxDowntime,
      tone: "progress-primary",
    },
    {
      key: "events",
      label: tx(locale, "eventLoad"),
      value: `${focusLine.events}`,
      score: focusLine.events,
      max: maxEvents,
      tone: "progress-info",
    },
    {
      key: "avg",
      label: tx(locale, "avgEvent"),
      value: `${focusLine.avg_event_hours.toFixed(1)}h`,
      score: focusLine.avg_event_hours,
      max: maxAvgHours,
      tone: "progress-warning",
    },
    {
      key: "missing",
      label: tx(locale, "missingData"),
      value: `${focusLine.missing_pct.toFixed(1)}%`,
      score: Math.min(focusLine.missing_pct, 100),
      max: 100,
      tone: "progress-error",
    },
  ];

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "triage")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "triageNote")}</h3>
            <p className="text-base-content/78 mt-3 text-sm">{tx(locale, "focusLineHint")}</p>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "priorityLines")}</div>
              <div className="stat-value text-2xl">{highPriority}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "avgRisk")}</div>
              <div className="stat-value text-2xl">{avgRisk.toFixed(1)}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "anomalyLines")}</div>
              <div className="stat-value text-2xl">{anomalyLines}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "worstMissing")}</div>
              <div className="stat-value text-xl">{worstMissing.line}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
                  {tx(locale, "focusLine")}
                </div>
                <h4 className="mt-2 text-2xl font-semibold">{focusLine.line}</h4>
                <p className="text-base-content/80 mt-2 text-sm">
                  {tx(locale, "topCause")}: <strong>{focusLine.top_category}</strong>
                </p>
              </div>
              <div className={`badge badge-lg ${priorityTone(focusLine.priority)}`}>{focusLine.priority}</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "riskScore")}</div>
                <div className="mt-3 text-3xl font-semibold">{focusLine.risk_score.toFixed(1)}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "downtimeHours")}</div>
                <div className="mt-3 text-3xl font-semibold">{focusLine.downtime_hours.toFixed(1)}h</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "eventLoad")}</div>
                <div className="mt-3 text-3xl font-semibold">{focusLine.events}</div>
              </div>
              <div className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "missingData")}</div>
                <div className="mt-3 text-3xl font-semibold">{focusLine.missing_pct.toFixed(1)}%</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button type="button" className="btn btn-primary" onClick={() => setFocusLine(rows[0].line)}>
                {tx(locale, "focusLine")}
              </button>
              <Link className="btn btn-outline" to={{ pathname: "/devices", search: devicesSearch.toString() }}>
                {tx(locale, "inspectDevices")}
              </Link>
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "lineQueue")}
            </div>
            <div className="space-y-3">
              {rows.map((row, index) => (
                <button
                  key={row.line}
                  type="button"
                  className={[
                    "w-full rounded-2xl border p-4 text-left transition-colors",
                    row.line === focusLine.line
                      ? "border-primary/35 bg-primary/10"
                      : "border-base-300/80 bg-base-200/45 hover:bg-base-200/70",
                  ].join(" ")}
                  onClick={() => setFocusLine(row.line)}
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="badge badge-primary badge-outline">{index + 1}</span>
                      <strong>{row.line}</strong>
                    </div>
                    <span className={`badge ${priorityTone(row.priority)}`}>{row.priority}</span>
                  </div>
                  <progress className="progress progress-primary h-2 w-full" value={row.risk_score} max={maxRisk} />
                  <div className="text-base-content/78 mt-3 flex flex-wrap gap-3 text-sm">
                    <span>{row.downtime_hours.toFixed(1)}h</span>
                    <span>{row.events} events</span>
                    <span>{row.missing_pct.toFixed(1)}%</span>
                    <span>{row.anomaly_count} anomalies</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "riskDrivers")}
            </div>
            <div className="space-y-3">
              {driverItems.map((item) => (
                <div key={item.key} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <span className="font-medium">{item.label}</span>
                    <strong>{item.value}</strong>
                  </div>
                  <progress className={`progress h-2 w-full ${item.tone}`} value={item.score} max={item.max} />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "responsePlaybook")}
            </div>
            <div className="space-y-3">
              {playbook.map((item, index) => (
                <div key={`${focusLine.line}-${index}`} className="rounded-2xl border border-base-300/80 bg-base-200/55 p-4">
                  <div className="mb-2 flex items-center gap-3">
                    <span className="badge badge-primary badge-outline">{index + 1}</span>
                    <strong>{tx(locale, "actionHint")}</strong>
                  </div>
                  <p className="text-base-content/82 text-sm">{item}</p>
                </div>
              ))}
            </div>
            <div className="alert alert-info">
              <span>
                {tx(locale, "riskScore")}: {focusLine.risk_score.toFixed(1)} · {tx(locale, "topCause")}: {focusLine.top_category}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="card border-base-300/70 bg-base-100 shadow-sm">
        <div className="card-body gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
            {tx(locale, "lineHealthTable")}
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Line</th>
                  <th>{tx(locale, "riskScore")}</th>
                  <th>{tx(locale, "downtimeHours")}</th>
                  <th>{tx(locale, "eventLoad")}</th>
                  <th>{tx(locale, "avgEvent")}</th>
                  <th>{tx(locale, "missingData")}</th>
                  <th>{tx(locale, "anomaliesLabel")}</th>
                  <th>{tx(locale, "status")}</th>
                  <th>{tx(locale, "topCause")}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.line}
                    className={row.line === focusLine.line ? "bg-primary/8 cursor-pointer" : "cursor-pointer"}
                    onClick={() => setFocusLine(row.line)}
                  >
                    <td>{row.line}</td>
                    <td>{row.risk_score.toFixed(1)}</td>
                    <td>{row.downtime_hours.toFixed(1)}h</td>
                    <td>{row.events}</td>
                    <td>{row.avg_event_hours.toFixed(1)}h</td>
                    <td>{row.missing_pct.toFixed(1)}%</td>
                    <td>{row.anomaly_count}</td>
                    <td>{row.priority}</td>
                    <td>{row.top_category}</td>
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
