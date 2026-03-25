import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState; themeMode: "light" | "dark" };

function priorityTone(priority: string) {
  const value = priority.toLowerCase();
  if (value.includes("high")) return "badge-error";
  if (value.includes("normal")) return "badge-warning";
  return "badge-info";
}

export function TasksPage() {
  const { locale, filters, themeMode } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["tasks", filters], queryFn: () => api.tasks(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;
  const topTask = data.rows[0];

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "tasks")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "tasksNote")}</h3>
          </div>

          <div className="stats stats-vertical lg:stats-horizontal border-base-300/60 bg-base-100/70 shadow-sm">
            <div className="stat">
              <div className="stat-title">{tx(locale, "topDevice")}</div>
              <div className="stat-value text-xl">{topTask?.device_name ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "dueDate")}</div>
              <div className="stat-value text-xl">{topTask?.due_date ?? "—"}</div>
            </div>
            <div className="stat">
              <div className="stat-title">{tx(locale, "status")}</div>
              <div className="stat-value text-xl">{topTask?.task_status || "—"}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        {data.kpis.map((kpi) => (
          <div key={kpi.id} className="stats border-base-300/70 bg-base-100 shadow-sm">
            <div className="stat">
              <div className="stat-title">
                {kpi.id === "overdue_tasks"
                  ? tx(locale, "overdueTasks")
                  : kpi.id === "high_priority"
                    ? tx(locale, "highPriorityTasks")
                    : kpi.id === "estimated_hours"
                      ? tx(locale, "estimatedHours")
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

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "priorityMix")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.priority_breakdown.map((item) => item.name),
            y: data.priority_breakdown.map((item) => item.value),
            name: "Tasks",
            color: "#ef4444",
          }}
        />
        <ChartPanel
          title={tx(locale, "serviceTypeMix")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.service_type_breakdown.map((item) => item.name),
            y: data.service_type_breakdown.map((item) => item.value),
            name: "Tasks",
            color: "#3b82f6",
          }}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <ChartPanel
          title={tx(locale, "overdueTrend")}
          themeMode={themeMode}
          series={{
            x: data.overdue_trend.map((item) => item.period),
            y: data.overdue_trend.map((item) => item.value),
            name: "Overdue %",
            color: "#f97316",
          }}
        />

        <div className="card border-base-300/70 bg-base-100 shadow-sm">
          <div className="card-body gap-4">
            <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">
              {tx(locale, "taskQueue")}
            </div>
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>{tx(locale, "devices")}</th>
                    <th>{tx(locale, "serviceHours")}</th>
                    <th>{tx(locale, "dueDate")}</th>
                    <th>{tx(locale, "assignedUsers")}</th>
                    <th>{tx(locale, "status")}</th>
                    <th>{tx(locale, "priorityMix")}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((row) => (
                    <tr key={row.task_id}>
                      <td>{row.task_number}</td>
                      <td>
                        <div className="font-medium">{row.device_name}</div>
                        <div className="text-base-content/70 text-xs">{row.line}</div>
                      </td>
                      <td>{row.service_name}</td>
                      <td>{row.due_date ?? "—"}</td>
                      <td>{row.assigned_users.join(", ") || "—"}</td>
                      <td>{row.task_status || "—"}</td>
                      <td>
                        <span className={`badge ${priorityTone(row.priority)}`}>{row.priority}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
