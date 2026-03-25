import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useOutletContext } from "react-router-dom";

import { api, type FiltersState } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { PageState } from "../../shared/ui/page-state";

type Context = { locale: Locale; filters: FiltersState; themeMode: "light" | "dark" };

function toneForSeverity(severity: "critical" | "warning" | "info") {
  if (severity === "critical") return "alert-error";
  if (severity === "warning") return "alert-warning";
  return "alert-info";
}

function trendPath(values: number[], width: number, height: number, offsetX = 0, offsetY = 0) {
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x = offsetX + (values.length === 1 ? width / 2 : (index / (values.length - 1)) * width);
      const y = offsetY + height - ((value - min) / range) * (height - 18) - 9;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

function TrendCard({
  title,
  themeMode,
  color,
  periods,
  values,
}: {
  title: string;
  themeMode: "light" | "dark";
  color: string;
  periods: string[];
  values: number[];
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const width = 640;
  const height = 220;
  const paddingX = 18;
  const paddingTop = 20;
  const chartHeight = 126;
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const range = max - min || 1;
  const path = trendPath(values, width - paddingX * 2, chartHeight, paddingX, paddingTop);
  const labelColor = themeMode === "dark" ? "rgba(255,255,255,0.68)" : "rgba(15,23,42,0.62)";
  const gridColor = themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.08)";
  const currentValue = values.at(-1) ?? 0;
  const currentLabel = periods[hoveredIndex ?? periods.length - 1] ?? "—";
  const step = values.length > 1 ? (width - paddingX * 2) / (values.length - 1) : 0;

  const pointX = (index: number) => paddingX + (values.length === 1 ? (width - paddingX * 2) / 2 : index * step);
  const pointY = (value: number) => paddingTop + (chartHeight - ((value - min) / range) * (chartHeight - 18) - 9);

  return (
    <section className="rounded-[1.6rem] border border-base-300/70 bg-base-100 shadow-sm">
      <div className="space-y-4 p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]">{title}</div>
          <div className="text-right">
            <div className="text-2xl font-semibold">{currentValue.toFixed(2)}h</div>
            <div className={`mt-1 text-xs ${themeMode === "dark" ? "text-white/65" : "text-slate-500"}`}>{currentLabel}</div>
          </div>
        </div>

        <div className="relative">
          {hoveredIndex !== null ? (
            <div
              className={`absolute right-2 top-2 z-10 rounded-xl border px-3 py-2 text-xs shadow-sm ${
                themeMode === "dark"
                  ? "border-white/10 bg-slate-950/88 text-white"
                  : "border-slate-200 bg-white/95 text-slate-900"
              }`}
            >
              <div className="font-semibold">{periods[hoveredIndex]}</div>
              <div className={themeMode === "dark" ? "mt-1 text-white/70" : "mt-1 text-slate-600"}>{values[hoveredIndex].toFixed(2)}h</div>
            </div>
          ) : null}

          <svg viewBox={`0 0 ${width} ${height}`} className="h-[220px] w-full">
            {[0, 1, 2, 3].map((index) => {
              const y = paddingTop + (chartHeight / 3) * index;
              return <line key={index} x1={paddingX} x2={width - paddingX} y1={y} y2={y} stroke={gridColor} strokeWidth="1" />;
            })}

            {hoveredIndex !== null ? (
              <line
                x1={pointX(hoveredIndex)}
                x2={pointX(hoveredIndex)}
                y1={paddingTop}
                y2={paddingTop + chartHeight}
                stroke={themeMode === "dark" ? "rgba(255,255,255,0.18)" : "rgba(15,23,42,0.16)"}
                strokeWidth="1"
                strokeDasharray="4 4"
              />
            ) : null}

            <path d={path} fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />

            {values.map((value, index) => (
              <g key={`${title}-${periods[index]}`}>
                <circle
                  cx={pointX(index)}
                  cy={pointY(value)}
                  r={hoveredIndex === index ? 5 : 3.2}
                  fill={color}
                  stroke={hoveredIndex === index ? (themeMode === "dark" ? "#ffffff" : "#0f172a") : "none"}
                  strokeWidth={hoveredIndex === index ? 1.4 : 0}
                />
                <rect
                  x={pointX(index) - Math.max(step / 2, 16)}
                  y={paddingTop}
                  width={Math.max(step, 32)}
                  height={chartHeight}
                  fill="transparent"
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                />
              </g>
            ))}

            {periods.map((period, index) => (
              <text
                key={`${title}-label-${period}`}
                x={pointX(index)}
                y={height - 10}
                textAnchor="end"
                transform={`rotate(-38 ${pointX(index)} ${height - 10})`}
                fontSize="11"
                fill={labelColor}
              >
                {period}
              </text>
            ))}
          </svg>
        </div>
      </div>
    </section>
  );
}

function DowntimeSplitCard({
  locale,
  themeMode,
  title,
  subtitle,
  items,
  totalHours,
}: {
  locale: Locale;
  themeMode: "light" | "dark";
  title: string;
  subtitle: string;
  items: Array<{ name: string; value: number; pct: number; color: string }>;
  totalHours: number;
}) {
  const [activeName, setActiveName] = useState<string | null>(null);
  const ringItems = items.filter((item) => item.value > 0);
  const total = ringItems.reduce((sum, item) => sum + item.value, 0) || 1;
  const dominant = ringItems[0] ?? { name: "—", value: 0, pct: 0, color: "#94a3b8" };
  const active = ringItems.find((item) => item.name === activeName) ?? dominant;
  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  const gap = ringItems.length > 1 ? 8 : 0;
  const drawable = Math.max(circumference - gap * ringItems.length, circumference * 0.74);
  const minArc = ringItems.length > 1 ? Math.min(28, drawable / ringItems.length / 1.5) : drawable;
  const raw = ringItems.map((item) => ({
    ...item,
    rawLength: (item.value / total) * drawable,
  }));
  const supportNeeded = raw.reduce((sum, item) => {
    if (item.rawLength >= minArc) return sum;
    return sum + (minArc - item.rawLength);
  }, 0);
  const donorPool = raw.reduce((sum, item) => {
    if (item.rawLength <= minArc) return sum;
    return sum + (item.rawLength - minArc);
  }, 0);

  let offset = 0;
  const segments = raw.map((item) => {
    let length = item.rawLength;
    if (item.rawLength < minArc) {
      length = minArc;
    } else if (supportNeeded > 0 && donorPool > 0) {
      const donation = ((item.rawLength - minArc) / donorPool) * supportNeeded;
      length = Math.max(minArc, item.rawLength - donation);
    }

    const segment = { ...item, length, offset };
    offset += length + gap;
    return segment;
  });

  return (
    <section
      className={[
        "overflow-hidden rounded-[1.8rem] border shadow-sm",
        themeMode === "dark"
          ? "border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(44,182,213,0.2),transparent_26%),radial-gradient(circle_at_82%_18%,rgba(255,71,139,0.14),transparent_24%),linear-gradient(180deg,#11131b_0%,#0b0d13_100%)] text-white"
          : "border-slate-200/80 bg-[radial-gradient(circle_at_top_left,rgba(44,182,213,0.14),transparent_28%),radial-gradient(circle_at_82%_18%,rgba(255,176,0,0.12),transparent_22%),linear-gradient(180deg,#ffffff_0%,#f5f8fb_100%)] text-slate-900",
      ].join(" ")}
    >
      <div className="space-y-5 p-6">
        <div className="space-y-2">
          <div className={themeMode === "dark" ? "text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-white/60" : "text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-slate-500"}>
            {title}
          </div>
          <div className={themeMode === "dark" ? "text-sm text-white/72" : "text-sm text-slate-600"}>{subtitle}</div>
        </div>

        <div className="grid gap-5 lg:grid-cols-[0.92fr_1.08fr] lg:items-center">
          <div className="relative flex items-center justify-center">
            <div
              className={[
                "absolute left-1/2 top-1 z-10 -translate-x-1/2 rounded-xl border px-3 py-2 text-xs shadow-sm transition-all",
                themeMode === "dark" ? "border-white/10 bg-slate-950/88 text-white" : "border-slate-200 bg-white/95 text-slate-900",
                activeName ? "opacity-100" : "pointer-events-none opacity-0",
              ].join(" ")}
            >
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: active.color }} />
                <span className="font-semibold">{active.name}</span>
              </div>
              <div className={themeMode === "dark" ? "mt-1 text-white/70" : "mt-1 text-slate-600"}>
                {active.value.toFixed(1)}h · {active.pct.toFixed(1)}%
              </div>
            </div>
            <div className="relative h-72 w-72">
              <svg viewBox="0 0 220 220" className="h-full w-full -rotate-90">
                <defs>
                  <filter id="overview-donut-glow" x="-40%" y="-40%" width="180%" height="180%">
                    <feGaussianBlur stdDeviation="2.4" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                <circle
                  cx="110"
                  cy="110"
                  r={radius}
                  fill="none"
                  stroke={themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.08)"}
                  strokeWidth="20"
                />
                {segments.map((item) => (
                  <circle
                    key={item.name}
                    cx="110"
                    cy="110"
                    r={radius}
                    fill="none"
                    stroke={item.color}
                    strokeWidth={active.name === item.name ? 22 : 20}
                    strokeLinecap="round"
                    strokeDasharray={`${item.length} ${Math.max(circumference - item.length, 1)}`}
                    strokeDashoffset={-item.offset}
                    filter="url(#overview-donut-glow)"
                    opacity={activeName === null || activeName === item.name ? 1 : 0.24}
                    style={{ cursor: "pointer", transition: "opacity 180ms ease, stroke-width 180ms ease" }}
                    onMouseEnter={() => setActiveName(item.name)}
                    onMouseLeave={() => setActiveName(null)}
                  />
                ))}
              </svg>
              <div
                className="absolute inset-[49px] grid place-items-center rounded-full border border-white/8 text-center shadow-inner"
                style={{
                  background:
                    themeMode === "dark"
                      ? "radial-gradient(circle at 50% 35%, rgba(255,255,255,0.08), rgba(15,23,42,0.92) 72%)"
                      : "radial-gradient(circle at 50% 35%, rgba(14,165,233,0.14), rgba(255,255,255,0.96) 72%)",
                }}
              >
                <div className="px-3">
                  <div className="text-4xl font-semibold tracking-tight">{totalHours.toFixed(0)}h</div>
                  <div className={themeMode === "dark" ? "mt-1 text-[11px] uppercase tracking-[0.14em] text-white/65" : "mt-1 text-[11px] uppercase tracking-[0.14em] text-slate-500"}>
                    {locale === "lv" ? "kopā" : "total"}
                  </div>
                  <div className={themeMode === "dark" ? "mt-3 text-sm font-medium text-cyan-100/85" : "mt-3 text-sm font-medium text-sky-700"}>
                    {active.name}
                  </div>
                  <div className={themeMode === "dark" ? "text-sm text-white/68" : "text-sm text-slate-600"}>{active.pct.toFixed(1)}%</div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {items.map((item) => (
              <button
                key={item.name}
                type="button"
                className={[
                  "w-full rounded-[1.3rem] border px-4 py-4 text-left transition-colors",
                  themeMode === "dark" ? "border-white/8 bg-white/[0.04] text-white" : "border-slate-200 bg-white/70 text-slate-900",
                  active.name === item.name
                    ? themeMode === "dark"
                      ? "border-cyan-200/35 bg-white/[0.07]"
                      : "border-sky-300 bg-sky-50"
                    : "",
                ].join(" ")}
                onMouseEnter={() => setActiveName(item.name)}
                onMouseLeave={() => setActiveName(null)}
                onClick={() => setActiveName((current) => (current === item.name ? null : item.name))}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="mt-1 h-3.5 w-3.5 rounded-full shadow-sm" style={{ backgroundColor: item.color }} />
                    <div>
                      <div className="text-base font-semibold">{item.name}</div>
                      <div className={themeMode === "dark" ? "mt-1 text-sm text-white/68" : "mt-1 text-sm text-slate-600"}>{item.pct.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-semibold">{item.value.toFixed(1)}h</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export function OverviewPage() {
  const { locale, filters, themeMode } = useOutletContext<Context>();
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
  const totalTypeHours = data.downtime_by_type.reduce((sum, item) => sum + item.value, 0);
  const typeBreakdown = data.downtime_by_type.map((item, index) => ({
    ...item,
    pct: totalTypeHours > 0 ? (item.value / totalTypeHours) * 100 : 0,
    color: ["#ff3b82", "#10d876", "#11b1c9", "#ff9f1a"][index % 4],
  }));

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
        <TrendCard
          title="MTTR"
          themeMode={themeMode}
          periods={data.mttr_trend.map((item) => item.period)}
          values={data.mttr_trend.map((item) => item.value)}
          color="#11b1c9"
        />
        <TrendCard
          title="MTBF"
          themeMode={themeMode}
          periods={data.mtbf_trend.map((item) => item.period)}
          values={data.mtbf_trend.map((item) => item.value)}
          color="#ff9f1a"
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
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

        <div className="space-y-4">
          <DowntimeSplitCard
            locale={locale}
            themeMode={themeMode}
            title={tx(locale, "downtimeSplitTitle")}
            subtitle={tx(locale, "downtimeMix")}
            totalHours={totalTypeHours}
            items={typeBreakdown}
          />

          <div className="grid gap-3 sm:grid-cols-2">
            {typeBreakdown.map((item) => (
              <div
                key={item.name}
                className={[
                  "rounded-[1.4rem] border p-4 shadow-sm transition-colors",
                  themeMode === "dark"
                    ? "border-white/8 bg-white/6 text-white"
                    : "border-base-300/80 bg-base-100 text-base-content",
                ].join(" ")}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span
                      className="mt-1 h-3.5 w-3.5 rounded-full shadow-sm"
                      style={{ backgroundColor: item.color }}
                    />
                    <div>
                      <div className={`text-base font-semibold ${themeMode === "dark" ? "text-white" : "text-base-content"}`}>{item.name}</div>
                      <div className={`mt-1 text-sm ${themeMode === "dark" ? "text-white/68" : "text-base-content/68"}`}>{item.pct.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-semibold ${themeMode === "dark" ? "text-white" : "text-base-content"}`}>{item.value.toFixed(1)}h</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
