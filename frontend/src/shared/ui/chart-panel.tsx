import { type ComponentType, lazy, Suspense } from "react";

function unwrapModule<T>(value: T): T {
  let current: unknown = value;

  while (
    current &&
    typeof current === "object" &&
    "default" in (current as Record<string, unknown>) &&
    (current as Record<string, unknown>).default !== current
  ) {
    current = (current as Record<string, unknown>).default;
  }

  return current as T;
}

const Plot = lazy(async () => {
  const [factoryModule, plotlyModule] = await Promise.all([
    import("react-plotly.js/factory.js"),
    import("plotly.js-basic-dist-min"),
  ]);
  const createPlotlyComponent = unwrapModule(factoryModule) as (
    plotly: unknown,
  ) => ComponentType<any>;
  const Plotly = unwrapModule(plotlyModule) as unknown;

  return { default: createPlotlyComponent(Plotly) as ComponentType<any> };
});

type Series = {
  x: string[];
  y: number[];
  name: string;
  color: string;
};

type Props = {
  title: string;
  series: Series;
  type?: "scatter" | "bar";
};

export function ChartPanel({ title, series, type = "scatter" }: Props) {
  return (
    <section className="card border-base-300/70 bg-base-100 shadow-sm">
      <div className="card-body gap-4">
        <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{title}</div>
        <Suspense
          fallback={
            <div className="bg-base-200 text-base-content/72 grid h-[280px] place-items-center rounded-2xl text-sm">
              Loading chart...
            </div>
          }
        >
        <Plot
          data={[
            {
              x: series.x,
              y: series.y,
              type,
              mode: type === "scatter" ? "lines+markers" : undefined,
              marker: { color: series.color },
              line: { color: series.color, width: 4 },
              fill: type === "scatter" ? "tozeroy" : undefined,
              name: series.name,
            },
          ]}
          layout={{
            autosize: true,
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { l: 32, r: 16, t: 8, b: 32 },
            font: { color: "#12222b" },
          }}
          style={{ width: "100%", height: "280px" }}
          config={{ displayModeBar: false, responsive: true }}
        />
        </Suspense>
      </div>
    </section>
  );
}
