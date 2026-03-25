import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { ChartPanel } from "../../shared/ui/chart-panel";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState; themeMode: "light" | "dark" };

export function CostsPage() {
  const { locale, filters, themeMode } = useOutletContext<Context>();
  const query = useQuery({ queryKey: ["costs", filters], queryFn: () => api.costs(filters) });

  if (query.isLoading) return <PageState kind="loading" message={tx(locale, "loading")} />;
  if (query.isError) return <PageState kind="error" message={tx(locale, "error")} />;
  if (!query.data) return <PageState kind="empty" message={tx(locale, "empty")} />;

  const data = query.data;

  return (
    <div className="space-y-5">
      <section className="hero rounded-[2rem] border border-base-300/70 bg-gradient-to-br from-base-100 via-base-100 to-primary/10 shadow-sm">
        <div className="hero-content w-full max-w-none justify-between gap-6 px-6 py-8">
          <div className="max-w-2xl">
            <div className="text-base-content/72 mb-3 text-xs font-semibold uppercase tracking-[0.24em]">
              {tx(locale, "costs")}
            </div>
            <h3 className="text-base-content text-3xl font-semibold tracking-tight">{tx(locale, "costsNote")}</h3>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
        {data.kpis.map((kpi) => (
          <div key={kpi.id} className="stats border-base-300/70 bg-base-100 shadow-sm">
            <div className="stat">
              <div className="stat-title">
                {kpi.id === "total_cost"
                  ? tx(locale, "totalCost")
                  : kpi.id === "extra_cost"
                    ? tx(locale, "extraCost")
                    : kpi.id === "spares_cost"
                      ? tx(locale, "sparesCost")
                      : tx(locale, "avgReportCost")}
              </div>
              <div className="stat-value text-4xl">{Number(kpi.value).toFixed(2)}</div>
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "monthlyCosts")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.monthly_total_costs.map((item) => item.period),
            y: data.monthly_total_costs.map((item) => item.value),
            name: tx(locale, "totalCost"),
            color: "#3b82f6",
          }}
        />
        <ChartPanel
          title={tx(locale, "costBreakdown")}
          type="bar"
          themeMode={themeMode}
          series={[
            {
              x: data.monthly_cost_breakdown.map((item) => item.period),
              y: data.monthly_cost_breakdown.map((item) => item.labor),
              name: locale === "lv" ? "Darbs" : "Labor",
              color: "#60a5fa",
              kind: "bar",
            },
            {
              x: data.monthly_cost_breakdown.map((item) => item.period),
              y: data.monthly_cost_breakdown.map((item) => item.extra),
              name: tx(locale, "extraCost"),
              color: "#f59e0b",
              kind: "bar",
            },
            {
              x: data.monthly_cost_breakdown.map((item) => item.period),
              y: data.monthly_cost_breakdown.map((item) => item.spares),
              name: tx(locale, "sparesCost"),
              color: "#ef4444",
              kind: "bar",
            },
          ]}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel
          title={tx(locale, "serviceCosts")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.service_costs.map((item) => item.name),
            y: data.service_costs.map((item) => item.value),
            name: tx(locale, "totalCost"),
            color: "#0ea5e9",
          }}
        />
        <ChartPanel
          title={tx(locale, "lineCosts")}
          type="bar"
          themeMode={themeMode}
          series={{
            x: data.line_costs.map((item) => item.name),
            y: data.line_costs.map((item) => item.value),
            name: tx(locale, "totalCost"),
            color: "#22c55e",
          }}
        />
      </section>
    </div>
  );
}
