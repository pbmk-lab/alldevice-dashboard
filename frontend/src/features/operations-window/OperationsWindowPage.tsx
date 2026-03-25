import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { api, type FiltersState, type SparkMetric } from "../../shared/api/client";
import { tx, type Locale } from "../../shared/i18n/translations";
import { DateRangePicker } from "../../shared/ui/date-range-picker";
import { PageState } from "../../shared/ui/page-state";
import { ThemeToggle } from "../../shared/ui/theme-toggle";

function metricLabel(locale: Locale, metric: SparkMetric) {
  switch (metric.id) {
    case "availability":
      return tx(locale, "metricAvailability");
    case "event_rate":
      return tx(locale, "metricEventRate");
    case "planned_share":
      return tx(locale, "metricPlannedShare");
    case "quality":
      return tx(locale, "metricQuality");
    default:
      return metric.label;
  }
}

function bucketLabel(locale: Locale, name: string) {
  if (name === "Overdue") return tx(locale, "bucketOverdue");
  if (name === "Today") return tx(locale, "bucketToday");
  if (name === "In progress") return tx(locale, "bucketInProgress");
  return name;
}

function panelClass(themeMode: "light" | "dark") {
  return themeMode === "dark"
    ? "rounded-[0.9rem] border border-white/8 bg-white/[0.035] text-white shadow-[0_18px_40px_rgba(0,0,0,0.22)]"
    : "rounded-[0.72rem] border border-slate-200 bg-white text-slate-900 shadow-[0_8px_24px_rgba(148,163,184,0.12)]";
}

function eyebrowClass(themeMode: "light" | "dark") {
  return themeMode === "dark"
    ? "text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-cyan-100/70"
    : "text-[0.66rem] font-semibold uppercase tracking-[0.16em] text-sky-800/80";
}

function bodyTextClass(themeMode: "light" | "dark") {
  return themeMode === "dark" ? "text-white/68" : "text-slate-600";
}

function sparkPath(values: number[], width = 240, height = 62) {
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return values
    .map((value, index) => {
      const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 10) - 5;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

function deriveWindowRange(maxDate: string, fallbackStart: string, explicitStart?: string | null, explicitEnd?: string | null) {
  if (explicitStart && explicitEnd) {
    return { start: explicitStart, end: explicitEnd };
  }

  const end = maxDate || explicitEnd || "";
  if (!end) {
    return { start: fallbackStart, end: explicitEnd ?? maxDate };
  }

  const yearStart = `${end.slice(0, 4)}-01-01`;
  return { start: yearStart, end };
}

function formatDurationHours(value: number, locale: Locale) {
  const totalHours = Math.max(value, 0);
  const days = Math.floor(totalHours / 24);
  const hours = Math.floor(totalHours % 24);

  if (days <= 0) {
    return `${totalHours.toFixed(1)}h`;
  }

  return locale === "lv" ? `${days}d ${hours}h` : `${days}d ${hours}h`;
}

function parseBoardIsoDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day, 12, 0, 0, 0);
}

function toBoardIsoDate(date: Date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addBoardDays(date: Date, value: number) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + value, 12, 0, 0, 0);
}

function clampIsoDate(value: string, min: string, max: string) {
  if (value < min) return min;
  if (value > max) return max;
  return value;
}

function endOfMonthIso(monthKey: string) {
  const [year, month] = monthKey.split("-").map(Number);
  const nextMonth = new Date(year, month, 1);
  const lastDay = new Date(nextMonth.getTime() - 24 * 60 * 60 * 1000);
  return toBoardIsoDate(lastDay);
}

function trailingDateKeys(endIso: string, count: number) {
  const end = parseBoardIsoDate(endIso);
  return Array.from({ length: count }, (_, index) => toBoardIsoDate(addBoardDays(end, -(count - 1 - index))));
}

function rangeFromCategoryKey(key: string, min: string, max: string) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(key)) {
    const clamped = clampIsoDate(key, min, max);
    return { start: clamped, end: clamped };
  }

  if (/^\d{4}-\d{2}$/.test(key)) {
    const start = clampIsoDate(`${key}-01`, min, max);
    const end = clampIsoDate(endOfMonthIso(key), min, max);
    return start <= end ? { start, end } : { start: end, end: start };
  }

  return null;
}

type BoardSeries = {
  name: string;
  values: number[];
  color: string;
  kind: "line" | "bar";
};

function boardTicks(minValue: number, maxValue: number) {
  const steps = 4;
  const span = maxValue - minValue || 1;
  return Array.from({ length: steps + 1 }, (_, index) => minValue + (span / steps) * index);
}

function formatCompactValue(value: number) {
  if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(1)}k`;
  return `${Math.round(value)}`;
}

function BoardChartCard({
  title,
  subtitle,
  categories,
  categoryKeys,
  series,
  themeMode,
  height = 250,
  onSelectCategory,
}: {
  title: string;
  subtitle: string;
  categories: string[];
  categoryKeys?: string[];
  series: BoardSeries[];
  themeMode: "light" | "dark";
  height?: number;
  onSelectCategory?: (key: string, index: number) => void;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const width = 760;
  const chartHeight = Math.max((height ?? 250) - 70, 170);
  const paddingLeft = 54;
  const paddingRight = 14;
  const paddingTop = 12;
  const paddingBottom = 38;
  const plotWidth = width - paddingLeft - paddingRight;
  const plotHeight = chartHeight - paddingTop - paddingBottom;
  const allValues = series.flatMap((item) => item.values);
  const rawMin = allValues.length ? Math.min(...allValues, 0) : 0;
  const rawMax = allValues.length ? Math.max(...allValues, 0) : 1;
  const yMin = rawMin;
  const yMax = rawMax === rawMin ? rawMin + 1 : rawMax;
  const ticks = boardTicks(yMin, yMax);
  const gridColor = themeMode === "dark" ? "rgba(255,255,255,0.09)" : "rgba(15,23,42,0.12)";
  const axisColor = themeMode === "dark" ? "rgba(255,255,255,0.45)" : "rgba(15,23,42,0.55)";
  const labelColor = themeMode === "dark" ? "rgba(255,255,255,0.72)" : "rgba(15,23,42,0.66)";
  const xStep = categories.length > 1 ? plotWidth / (categories.length - 1) : plotWidth / 2;
  const baselineY = paddingTop + ((yMax - 0) / (yMax - yMin || 1)) * plotHeight;
  const tooltipLabel = hoveredIndex !== null ? categories[hoveredIndex] : null;

  const yForValue = (value: number) => paddingTop + ((yMax - value) / (yMax - yMin || 1)) * plotHeight;
  const xForIndex = (index: number) => paddingLeft + (categories.length === 1 ? plotWidth / 2 : xStep * index);

  return (
    <section className={panelClass(themeMode)}>
      <div className="px-5 py-5">
        <div className={eyebrowClass(themeMode)}>{title}</div>
        <div className={`mt-2 text-sm ${bodyTextClass(themeMode)}`}>{subtitle}</div>
        <div className="relative mt-4">
          {tooltipLabel ? (
            <div
              className={`absolute right-2 top-2 z-10 rounded-xl border px-3 py-2 text-xs shadow-sm ${
                themeMode === "dark"
                  ? "border-white/10 bg-slate-950/88 text-white"
                  : "border-slate-200 bg-white/95 text-slate-900"
              }`}
            >
              <div className="font-semibold">{tooltipLabel}</div>
              <div className="mt-1 space-y-1">
                {series.map((item) => (
                  <div key={`${tooltipLabel}-${item.name}`} className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span>{item.name}: {item.values[hoveredIndex ?? 0] ?? 0}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
          <svg viewBox={`0 0 ${width} ${chartHeight}`} className="h-[180px] w-full">
            {ticks.map((tick) => {
              const y = yForValue(tick);
              return (
                <g key={tick}>
                  <line x1={paddingLeft} x2={width - paddingRight} y1={y} y2={y} stroke={gridColor} strokeWidth="1" />
                  <text x={paddingLeft - 8} y={y + 4} textAnchor="end" fontSize="11" fill={labelColor}>
                    {formatCompactValue(tick)}
                  </text>
                </g>
              );
            })}

            <line x1={paddingLeft} x2={paddingLeft} y1={paddingTop} y2={paddingTop + plotHeight} stroke={axisColor} strokeWidth="1.2" />
            <line x1={paddingLeft} x2={width - paddingRight} y1={baselineY} y2={baselineY} stroke={axisColor} strokeWidth="1.2" />
            {hoveredIndex !== null ? (
              <line
                x1={xForIndex(hoveredIndex)}
                x2={xForIndex(hoveredIndex)}
                y1={paddingTop}
                y2={paddingTop + plotHeight}
                stroke={themeMode === "dark" ? "rgba(255,255,255,0.2)" : "rgba(15,23,42,0.18)"}
                strokeWidth="1"
                strokeDasharray="4 4"
              />
            ) : null}

            {series.map((item, seriesIndex) => {
              if (item.kind === "bar") {
                const barSeriesCount = series.filter((entry) => entry.kind === "bar").length;
                const barIndex = series.filter((entry, index) => entry.kind === "bar" && index <= seriesIndex).length - 1;
                const clusterWidth = Math.min(28, plotWidth / Math.max(categories.length, 1) / 1.6);
                const singleBarWidth = Math.max(clusterWidth / Math.max(barSeriesCount, 1), 8);

                return item.values.map((value, index) => {
                  const centerX = xForIndex(index);
                  const x = centerX - clusterWidth / 2 + barIndex * singleBarWidth;
                  const y = Math.min(yForValue(value), baselineY);
                  const barHeight = Math.abs(baselineY - yForValue(value));
                  return (
                    <rect
                      key={`${item.name}-${index}`}
                      x={x}
                      y={y}
                      width={singleBarWidth - 2}
                      height={Math.max(barHeight, 1)}
                      rx="1.5"
                      fill={item.color}
                      opacity={hoveredIndex === null || hoveredIndex === index ? 0.98 : 0.68}
                      style={{ cursor: onSelectCategory ? "pointer" : "default" }}
                      onClick={() => {
                        const key = categoryKeys?.[index] ?? categories[index];
                        if (key && onSelectCategory) onSelectCategory(key, index);
                      }}
                    />
                  );
                });
              }

              const path = item.values
                .map((value, index) => `${index === 0 ? "M" : "L"} ${xForIndex(index)} ${yForValue(value)}`)
                .join(" ");
              return (
                <g key={item.name}>
                  <path d={path} fill="none" stroke={item.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                  {item.values.map((value, index) => (
                    <circle
                      key={`${item.name}-${index}`}
                      cx={xForIndex(index)}
                      cy={yForValue(value)}
                      r={hoveredIndex === index ? 4.8 : 3}
                      fill={item.color}
                      stroke={hoveredIndex === index ? (themeMode === "dark" ? "#ffffff" : "#0f172a") : "none"}
                      strokeWidth={hoveredIndex === index ? 1.5 : 0}
                      style={{ cursor: onSelectCategory ? "pointer" : "default" }}
                      onClick={() => {
                        const key = categoryKeys?.[index] ?? categories[index];
                        if (key && onSelectCategory) onSelectCategory(key, index);
                      }}
                    />
                  ))}
                </g>
              );
            })}

            {categories.map((label, index) => {
              const currentX = xForIndex(index);
              const previousX = index > 0 ? xForIndex(index - 1) : paddingLeft;
              const nextX = index < categories.length - 1 ? xForIndex(index + 1) : width - paddingRight;
              const zoneWidth = categories.length === 1 ? plotWidth : nextX - previousX;
              const zoneX = categories.length === 1 ? paddingLeft : currentX - zoneWidth / 2;

              return (
                <rect
                  key={`hover-${label}-${index}`}
                  x={zoneX}
                  y={paddingTop}
                  width={Math.max(zoneWidth, 18)}
                  height={plotHeight}
                  fill="transparent"
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  style={{ cursor: onSelectCategory ? "pointer" : "default" }}
                  onClick={() => {
                    const key = categoryKeys?.[index] ?? categories[index];
                    if (key && onSelectCategory) onSelectCategory(key, index);
                  }}
                />
              );
            })}

            {categories.map((label, index) => (
              <text
                key={`${label}-${index}`}
                x={xForIndex(index)}
                y={chartHeight - 10}
                textAnchor="end"
                transform={`rotate(-40 ${xForIndex(index)} ${chartHeight - 10})`}
                fontSize="11"
                fill={labelColor}
              >
                {label}
              </text>
            ))}
          </svg>
        </div>

        {series.length > 1 ? (
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs">
            {series.map((item) => (
              <div key={item.name} className={`flex items-center gap-2 ${bodyTextClass(themeMode)}`}>
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function StatusDonutCard({
  locale,
  themeMode,
  title,
  items,
  tasks,
  openDurations,
}: {
  locale: Locale;
  themeMode: "light" | "dark";
  title: string;
  items: Array<{ name: string; value: number; color: string }>;
  tasks: Array<{
    task_id: number;
    task_number: string;
    device_name: string;
    due_date?: string | null;
    status_bucket?: string | null;
  }>;
  openDurations: number[];
}) {
  const [activeName, setActiveName] = useState<string | null>(null);
  const total = items.reduce((sum, item) => sum + item.value, 0);
  const normalized = total > 0 ? items : [{ name: "Overdue", value: 1, color: "#2f3642" }];
  const circumference = 2 * Math.PI * 54;
  const visibleItems = normalized.filter((item) => item.value > 0);
  const gapArc = visibleItems.length > 1 ? 6 : 0;
  const totalGapArc = gapArc * visibleItems.length;
  const drawableArc = Math.max(circumference - totalGapArc, circumference * 0.72);
  const longestOpen = openDurations.length ? Math.max(...openDurations) : 0;
  const dominantItem = normalized.reduce((top, item) => (item.value > top.value ? item : top), normalized[0]);
  const dominantPct = total > 0 ? (dominantItem.value / total) * 100 : 0;
  const filterBase = `status-donut-${title.replace(/[^a-zA-Z0-9]/g, "").toLowerCase() || "default"}`;
  const activeItem = normalized.find((item) => item.name === activeName) ?? dominantItem;
  const activePct = total > 0 ? (activeItem.value / total) * 100 : 0;
  const filteredTasks = tasks
    .filter((row) => (activeName ? row.status_bucket === activeName : row.status_bucket === activeItem.name))
    .slice(0, 4);
  const positiveTotal = visibleItems.reduce((sum, item) => sum + item.value, 0) || 1;
  const minVisibleArc = visibleItems.length > 1 ? Math.min(26, drawableArc / visibleItems.length / 1.6) : drawableArc;
  const rawSegments = normalized.map((item) => ({
    ...item,
    rawLength: item.value > 0 ? (item.value / positiveTotal) * drawableArc : 0,
  }));
  const supportNeeded = rawSegments.reduce((sum, item) => {
    if (item.value <= 0 || item.rawLength >= minVisibleArc) return sum;
    return sum + (minVisibleArc - item.rawLength);
  }, 0);
  const donorPool = rawSegments.reduce((sum, item) => {
    if (item.value <= 0 || item.rawLength <= minVisibleArc) return sum;
    return sum + (item.rawLength - minVisibleArc);
  }, 0);

  let offset = 0;
  const segments = rawSegments.map((item) => {
    let adjustedLength = item.rawLength;

    if (item.value > 0 && item.rawLength < minVisibleArc) {
      adjustedLength = minVisibleArc;
    } else if (item.value > 0 && supportNeeded > 0 && donorPool > 0 && item.rawLength > minVisibleArc) {
      const donationShare = ((item.rawLength - minVisibleArc) / donorPool) * supportNeeded;
      adjustedLength = Math.max(minVisibleArc, item.rawLength - donationShare);
    }

    const segment = {
      ...item,
      length: adjustedLength,
      gap: item.value > 0 ? gapArc : 0,
      offset,
    };
    offset += adjustedLength + (item.value > 0 ? gapArc : 0);
    return segment;
  });

  return (
    <section className={`${panelClass(themeMode)} h-full`}>
      <div className="flex min-h-[470px] flex-col px-5 py-5">
        <div className={eyebrowClass(themeMode)}>{title}</div>
        <div className="mt-3 grid flex-1 gap-4 lg:grid-cols-[0.78fr_1.22fr] lg:items-center">
          <div className="relative grid place-items-center">
            <div
              className={`absolute left-1/2 top-0 z-10 -translate-x-1/2 -translate-y-1/2 rounded-xl border px-3 py-2 text-xs shadow-sm transition-all ${
                themeMode === "dark"
                  ? "border-white/10 bg-slate-950/88 text-white"
                  : "border-slate-200 bg-white/95 text-slate-900"
              } ${activeName ? "opacity-100" : "pointer-events-none opacity-0"}`}
            >
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: activeItem.color }} />
                <span className="font-semibold">{bucketLabel(locale, activeItem.name)}</span>
              </div>
              <div className={`mt-1 ${bodyTextClass(themeMode)}`}>
                {activeItem.value.toFixed(0)} · {activePct.toFixed(1)}%
              </div>
            </div>
            <div className="relative h-36 w-36">
              <svg viewBox="0 0 140 140" className="h-full w-full -rotate-90">
                <defs>
                  <filter id={`${filterBase}-glow`} x="-40%" y="-40%" width="180%" height="180%">
                    <feGaussianBlur stdDeviation="2.4" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <radialGradient id={`${filterBase}-core`} cx="50%" cy="45%" r="65%">
                    <stop offset="0%" stopColor={themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(14,165,233,0.12)"} />
                    <stop offset="100%" stopColor={themeMode === "dark" ? "rgba(255,255,255,0.01)" : "rgba(255,255,255,0.92)"} />
                  </radialGradient>
                </defs>
                <circle
                  cx="70"
                  cy="70"
                  r="60"
                  fill="none"
                  stroke={themeMode === "dark" ? "rgba(56,189,248,0.08)" : "rgba(14,165,233,0.08)"}
                  strokeWidth="5"
                />
                <circle cx="70" cy="70" r="54" fill="none" stroke={themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.08)"} strokeWidth="16" />
                {segments.map((item) => (
                  <circle
                    key={`${item.name}-${item.value}`}
                    cx="70"
                    cy="70"
                    r="54"
                    fill="none"
                    stroke={item.color}
                    strokeWidth="16"
                    strokeLinecap="round"
                    strokeDasharray={`${item.length} ${Math.max(circumference - item.length, 1)}`}
                    strokeDashoffset={-item.offset}
                    filter={`url(#${filterBase}-glow)`}
                    opacity={activeName === null || activeName === item.name ? 1 : 0.28}
                    style={{ cursor: "pointer", transition: "opacity 180ms ease, stroke-width 180ms ease" }}
                    onMouseEnter={() => setActiveName(item.name)}
                    onMouseLeave={() => setActiveName(null)}
                  />
                ))}
              </svg>
              <div
                className="absolute inset-[22px] grid place-items-center rounded-full border border-white/6 text-center shadow-inner"
                style={{
                  background:
                    themeMode === "dark"
                      ? "radial-gradient(circle at 50% 35%, rgba(255,255,255,0.08), rgba(15,23,42,0.92) 72%)"
                      : "radial-gradient(circle at 50% 35%, rgba(14,165,233,0.16), rgba(255,255,255,0.96) 72%)",
                }}
              >
                <div className="px-2">
                  <div className="text-4xl font-semibold tracking-tight">{total}</div>
                  <div className={`mt-1 text-[11px] uppercase tracking-[0.14em] ${bodyTextClass(themeMode)}`}>{tx(locale, "status")}</div>
                  <div className={`mt-2 text-[11px] font-medium ${themeMode === "dark" ? "text-cyan-100/80" : "text-sky-700"}`}>
                    {bucketLabel(locale, activeItem.name)}
                  </div>
                  <div className={`text-[11px] ${bodyTextClass(themeMode)}`}>{(activeName ? activePct : dominantPct).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            {items.map((item) => {
              const pct = total > 0 ? (item.value / total) * 100 : 0;
              return (
                <div
                  key={item.name}
                  className={[
                    themeMode === "dark"
                      ? "rounded-2xl border border-white/8 bg-white/[0.03] px-3.5 py-2.5"
                      : "rounded-2xl border border-slate-200 bg-slate-50 px-3.5 py-2.5",
                    activeName === item.name
                      ? themeMode === "dark"
                        ? "border-cyan-200/35 bg-white/[0.06]"
                        : "border-sky-300 bg-sky-50"
                      : "",
                  ].join(" ")}
                  onMouseEnter={() => setActiveName(item.name)}
                  onMouseLeave={() => setActiveName(null)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <div>
                        <div className="text-sm font-medium">{bucketLabel(locale, item.name)}</div>
                        <div className={`text-[11px] ${bodyTextClass(themeMode)}`}>{pct.toFixed(1)}%</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">{item.value.toFixed(0)}</div>
                    </div>
                  </div>
                </div>
              );
            })}

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div className={themeMode === "dark" ? "rounded-2xl border border-white/8 bg-white/[0.03] px-3.5 py-2.5" : "rounded-2xl border border-slate-200 bg-slate-50 px-3.5 py-2.5"}>
                <div className={`text-[0.64rem] font-semibold uppercase tracking-[0.12em] ${bodyTextClass(themeMode)}`}>{tx(locale, "openCount")}</div>
                <div className="mt-1.5 text-lg font-semibold">{total}</div>
              </div>
              <div className={themeMode === "dark" ? "rounded-2xl border border-white/8 bg-white/[0.03] px-3.5 py-2.5" : "rounded-2xl border border-slate-200 bg-slate-50 px-3.5 py-2.5"}>
                <div className={`text-[0.64rem] font-semibold uppercase tracking-[0.12em] ${bodyTextClass(themeMode)}`}>{tx(locale, "longestOpen")}</div>
                <div className="mt-1.5 text-lg font-semibold">{formatDurationHours(longestOpen, locale)}</div>
              </div>
            </div>
          </div>
        </div>

        <div className={`mt-4 rounded-2xl border px-4 py-3 ${themeMode === "dark" ? "border-white/8 bg-white/[0.025]" : "border-slate-200 bg-slate-50/75"}`}>
          <div className="mb-3 flex items-center justify-between gap-3">
            <div className={eyebrowClass(themeMode)}>{tx(locale, "taskQueue")}</div>
            <div className={`text-xs ${bodyTextClass(themeMode)}`}>
              {bucketLabel(locale, activeItem.name)}
            </div>
          </div>

          {filteredTasks.length ? (
            <div className="space-y-2">
              {filteredTasks.map((row) => (
                <div
                  key={row.task_id}
                  className={themeMode === "dark" ? "rounded-xl border border-white/6 bg-white/[0.025] px-3 py-2" : "rounded-xl border border-slate-200 bg-white px-3 py-2"}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{row.device_name}</div>
                      <div className={`truncate text-[11px] ${bodyTextClass(themeMode)}`}>{row.task_number}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">{row.due_date ?? "—"}</div>
                      <div className={`text-[11px] ${bodyTextClass(themeMode)}`}>{bucketLabel(locale, row.status_bucket ?? activeItem.name)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={`rounded-xl border px-3 py-4 text-sm ${themeMode === "dark" ? "border-white/6 bg-white/[0.02] text-white/68" : "border-slate-200 bg-white text-slate-600"}`}>
              {tx(locale, "empty")}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function SparkCard({
  metric,
  locale,
  themeMode,
}: {
  metric: SparkMetric;
  locale: Locale;
  themeMode: "light" | "dark";
}) {
  const path = sparkPath(metric.trend);
  const value = `${metric.value.toFixed(2)}${metric.suffix ? metric.suffix : ""}`;

  return (
    <article
      className={[
        "rounded-[0.95rem] border px-3 py-2.5 shadow-sm",
        themeMode === "dark"
          ? "border-white/8 bg-white/[0.035] text-white"
          : "border-slate-200/90 bg-white text-slate-900",
      ].join(" ")}
    >
      <div className="mb-1.5 flex items-center justify-between gap-3">
        <div
          className={`text-[0.66rem] font-semibold uppercase tracking-[0.14em] ${
            themeMode === "dark" ? "text-white/55" : "text-sky-800/85"
          }`}
        >
          {metricLabel(locale, metric)}
        </div>
        <div className="text-[1.05rem] font-semibold tracking-tight">{value}</div>
      </div>
      <svg viewBox="0 0 240 62" className="h-10 w-full overflow-visible">
        <defs>
          <linearGradient id={`spark-${metric.id}`} x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor={themeMode === "dark" ? "#6ee7f9" : "#0ea5e9"} />
            <stop offset="100%" stopColor={themeMode === "dark" ? "#7ea6ff" : "#2563eb"} />
          </linearGradient>
        </defs>
        <path
          d={path}
          fill="none"
          stroke={`url(#spark-${metric.id})`}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </article>
  );
}

export function OperationsWindowPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const bootstrap = useQuery({ queryKey: ["filters-bootstrap-window"], queryFn: api.filters });
  const [themeMode, setThemeMode] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    return window.localStorage.getItem("operations-window-theme") === "dark" ? "dark" : "light";
  });

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem("operations-window-theme", themeMode);
  }, [themeMode]);

  const bootstrapData = bootstrap.data;
  const allLines = bootstrapData?.lines ?? [];
  const locale = (searchParams.get("locale") as Locale | null) ?? bootstrapData?.default_locale ?? "lv";
  const lineMode = searchParams.get("line_mode") ?? "all";
  const selectedLines = searchParams.getAll("lines");
  const activeLines = lineMode === "none" ? [] : lineMode === "custom" ? selectedLines : allLines;
  const filterLines = lineMode === "none" ? ["__no_line_selected__"] : activeLines;
  const resolvedRange = deriveWindowRange(
    bootstrapData?.max_date ?? "",
    bootstrapData?.default_start ?? "",
    searchParams.get("date_start"),
    searchParams.get("date_end"),
  );
  const dateStart = resolvedRange.start;
  const dateEnd = resolvedRange.end;
  const filters: FiltersState = {
    locale,
    dateStart,
    dateEnd,
    lines: filterLines,
  };

  const boardQuery = useQuery({
    enabled: Boolean(bootstrapData && dateStart && dateEnd),
    queryKey: ["operations-window", filters],
    queryFn: () => api.operationsWindow(filters),
  });
  const tasksQuery = useQuery({
    enabled: Boolean(bootstrapData && dateStart && dateEnd),
    queryKey: ["operations-window-tasks", filters],
    queryFn: () => api.tasks(filters),
  });
  const costsQuery = useQuery({
    enabled: Boolean(bootstrapData && dateStart && dateEnd),
    queryKey: ["operations-window-costs", filters],
    queryFn: () => api.costs(filters),
  });

  const patchParams = (patch: Record<string, string>) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(patch).forEach(([key, value]) => {
      next.set(key, value);
    });
    setSearchParams(next, { replace: true });
  };

  const focusCategory = (key: string) => {
    if (!bootstrapData) return;
    const nextRange = rangeFromCategoryKey(key, bootstrapData.min_date, bootstrapData.max_date);
    if (!nextRange) return;
    patchParams({ date_start: nextRange.start, date_end: nextRange.end });
  };

  if (bootstrap.isLoading || (bootstrapData && (boardQuery.isLoading || tasksQuery.isLoading || costsQuery.isLoading))) {
    return (
      <main data-theme={themeMode === "dark" ? "business" : "corporate"} className="min-h-screen p-6">
        <PageState kind="loading" message={tx(locale, "loading")} />
      </main>
    );
  }

  if (bootstrap.isError || boardQuery.isError || tasksQuery.isError || costsQuery.isError) {
    return (
      <main data-theme={themeMode === "dark" ? "business" : "corporate"} className="min-h-screen p-6">
        <PageState kind="error" message={tx(locale, "error")} />
      </main>
    );
  }

  if (!bootstrapData || !boardQuery.data || !tasksQuery.data || !costsQuery.data) {
    return (
      <main data-theme={themeMode === "dark" ? "business" : "corporate"} className="min-h-screen p-6">
        <PageState kind="empty" message={tx(locale, "empty")} />
      </main>
    );
  }

  const data = boardQuery.data;
  const taskBoard = tasksQuery.data;
  const costsBoard = costsQuery.data;
  const taskStatusBuckets = Array.isArray((taskBoard as { status_buckets?: unknown }).status_buckets)
    ? taskBoard.status_buckets
    : [];
  const taskDistributionTrend = Array.isArray((taskBoard as { distribution_trend?: unknown }).distribution_trend)
    ? taskBoard.distribution_trend
    : [];
  const costBreakdown = Array.isArray((costsBoard as { monthly_cost_breakdown?: unknown }).monthly_cost_breakdown)
    ? costsBoard.monthly_cost_breakdown
    : [];

  const activeTaskSeries = taskStatusBuckets.length
    ? taskStatusBuckets.map((item, index) => ({
        name: item.name,
        value: item.value,
        color: [ "#ff6b77", "#7ea6ff", "#c9ccd3" ][index] ?? "#c9ccd3",
      }))
    : data.task_status;
  const primaryMetrics = data.spark_metrics.slice(0, 4);
  const secondaryMetrics = data.spark_metrics.slice(4);
  const hasPlannedActualData = data.planned_vs_actual.some((item) => item.planned > 0 || item.actual > 0);
  const hasTaskDistributionData = taskDistributionTrend.some(
    (item) => item.emergency > 0 || item.planned > 0 || item.regular > 0,
  );
  const hasCostData = costBreakdown.some(
    (item) => item.labor > 0 || item.extra > 0 || item.spares > 0,
  );
  const hasOverdueTrendData = taskBoard.overdue_trend.some((item) => item.value !== 0);
  const hasWorkHoursData = data.work_hours_12m.some((item) => item.value > 0);
  const hasMonthlyCostTotals = costsBoard.monthly_total_costs.some((item) => item.value > 0);

  return (
    <main
      data-theme={themeMode === "dark" ? "business" : "corporate"}
      className={[
        "min-h-screen px-3 py-3 text-base-content sm:px-4 lg:px-5",
        themeMode === "dark"
          ? "bg-[#18191d]"
          : "bg-[#eef1f7]",
      ].join(" ")}
    >
      <div className="mx-auto flex max-w-[1820px] flex-col gap-2.5">
        <section
          className={[
            "rounded-[0.85rem] border px-4 py-3 shadow-sm",
            themeMode === "dark"
              ? "border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(44,182,213,0.18),transparent_28%),linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02))] text-white shadow-[0_18px_40px_rgba(0,0,0,0.24)]"
              : "border-slate-200 bg-white text-slate-900 shadow-[0_10px_28px_rgba(148,163,184,0.14)]",
          ].join(" ")}
        >
          <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
            <div className="space-y-2">
              <div
                className={`text-[0.68rem] font-semibold uppercase tracking-[0.22em] ${
                  themeMode === "dark" ? "text-white/55" : "text-sky-800/80"
                }`}
              >
                {tx(locale, "operationsWindow")}
              </div>
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">{tx(locale, "boardHeroTitle")}</h1>
                <p className={`mt-1 max-w-4xl text-sm leading-5 ${themeMode === "dark" ? "text-white/68" : "text-slate-600"}`}>
                  {tx(locale, "boardHeroHint")}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <div className={`rounded-[0.2rem] border px-3 py-1 text-sm ${themeMode === "dark" ? "border-white/25 bg-white/[0.04]" : "border-slate-300 bg-white"}`}>{dateStart} → {dateEnd}</div>
                <div className={`rounded-[0.2rem] px-3 py-1 text-sm ${themeMode === "dark" ? "bg-white/[0.05] text-cyan-200/85" : "bg-slate-100 text-slate-700"}`}>
                  {activeLines.length || allLines.length} {tx(locale, "lines").toLowerCase()}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 xl:self-center">
              <ThemeToggle mode={themeMode} onChange={setThemeMode} compact />
              <div className="join">
                {(["lv", "en"] as const).map((item) => (
                  <button
                    key={item}
                    className={`btn btn-sm join-item ${item === locale ? "btn-primary" : "btn-outline"}`}
                    onClick={() => patchParams({ locale: item })}
                  >
                    {item.toUpperCase()}
                  </button>
                ))}
              </div>
              <Link className="btn btn-sm btn-outline" to={{ pathname: "/", search: searchParams.toString() }}>
                {tx(locale, "backToDashboard")}
              </Link>
            </div>
          </div>

          <div className="mt-4 max-w-md">
            <DateRangePicker
              locale={locale}
              start={dateStart}
              end={dateEnd}
              min={bootstrapData.min_date}
              max={bootstrapData.max_date}
              onChange={(nextStart, nextEnd) => patchParams({ date_start: nextStart, date_end: nextEnd })}
            />
          </div>
        </section>

        <section className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
          {primaryMetrics.map((metric) => (
            <SparkCard key={metric.id} metric={metric} locale={locale} themeMode={themeMode} />
          ))}
        </section>

        {secondaryMetrics.length ? (
          <section className="grid gap-2 xl:grid-cols-2">
            {secondaryMetrics.map((metric) => (
              <SparkCard key={metric.id} metric={metric} locale={locale} themeMode={themeMode} />
            ))}
          </section>
        ) : null}

        <section className="grid gap-2.5 xl:grid-cols-[1.05fr_1.05fr_1fr]">
          <div className="min-h-0">
            {activeTaskSeries.some((item) => item.value > 0) ? (
              <StatusDonutCard
                locale={locale}
                themeMode={themeMode}
                title={tx(locale, "activeTasks")}
                items={activeTaskSeries}
                tasks={taskBoard.rows}
                openDurations={data.open_downtimes.map((item) => item.duration_hours)}
              />
            ) : (
              <section className={panelClass(themeMode)}>
                <div className="flex h-[305px] flex-col justify-between px-6 py-5">
                  <div className={eyebrowClass(themeMode)}>
                    {tx(locale, "activeTasks")}
                  </div>
                  <div className="grid flex-1 place-items-center">
                    <div className="space-y-4 text-center">
                      <div className="mx-auto grid h-24 w-24 place-items-center rounded-full border border-dashed border-current/25">
                        <div className="h-10 w-10 rounded-full bg-current/10" />
                      </div>
                      <div>
                        <div className="text-lg font-semibold">{tx(locale, "activeTasks")}</div>
                        <p className={`mt-2 max-w-xs text-sm leading-6 ${bodyTextClass(themeMode)}`}>
                          {tx(locale, "noOpenDowntimes")}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}
          </div>

          <section className={panelClass(themeMode)}>
            <div className="px-5 py-5">
              <div className={eyebrowClass(themeMode)}>
                {tx(locale, "problemDevices")}
              </div>
              {data.problem_devices.length ? (
                <div className="overflow-x-auto">
                  <table className="mt-3 w-full text-left text-[12px]">
                    <thead>
                      <tr className={themeMode === "dark" ? "text-white/55" : "text-slate-500"}>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "devices")}</th>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "incidents")}</th>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "lastIssue")}</th>
                        <th className="pb-2 pr-3 font-semibold">MTBF</th>
                        <th className="pb-2 font-semibold">MTTR</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.problem_devices.map((row) => (
                        <tr
                          key={row.device_name}
                          className={themeMode === "dark" ? "border-t border-white/6" : "border-t border-slate-200/75"}
                        >
                          <td className="max-w-[14rem] py-2.5 pr-3 font-medium">{row.device_name}</td>
                          <td className="py-2.5 pr-3">{row.incidents}</td>
                          <td className={`py-2.5 pr-3 ${bodyTextClass(themeMode)}`}>{row.last_issue ?? "—"}</td>
                          <td className={`py-2.5 pr-3 ${bodyTextClass(themeMode)}`}>{row.mtbf_hours.toFixed(1)}h</td>
                          <td className={`py-2.5 ${bodyTextClass(themeMode)}`}>{row.mttr_hours.toFixed(1)}h</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className={`mt-4 rounded-2xl border px-4 py-4 text-sm ${themeMode === "dark" ? "border-white/8 bg-white/[0.03] text-white/72" : "border-slate-200 bg-slate-50 text-slate-600"}`}>{tx(locale, "noProblemDevices")}</div>
              )}
            </div>
          </section>

          <section className={panelClass(themeMode)}>
            <div className="px-5 py-5">
              <div className={eyebrowClass(themeMode)}>
                {tx(locale, "openDowntimes")}
              </div>
              {data.open_downtimes.length ? (
                <div className="overflow-x-auto">
                  <table className="mt-3 w-full text-left text-[12px]">
                    <thead>
                      <tr className={themeMode === "dark" ? "text-white/55" : "text-slate-500"}>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "devices")}</th>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "lastService")}</th>
                        <th className="pb-2 pr-3 font-semibold">{tx(locale, "startedAt")}</th>
                        <th className="pb-2 font-semibold">{tx(locale, "duration")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.open_downtimes.map((row, index) => (
                        <tr
                          key={`${row.device_name}-${row.started_at ?? index}`}
                          className={themeMode === "dark" ? "border-t border-white/6" : "border-t border-slate-200/75"}
                        >
                          <td className="py-2.5 pr-3">
                            <div className="font-medium">{row.device_name}</div>
                            <div className={`text-[11px] ${bodyTextClass(themeMode)}`}>{row.line}</div>
                          </td>
                          <td className={`py-2.5 pr-3 ${bodyTextClass(themeMode)}`}>{row.last_service ?? "—"}</td>
                          <td className={`py-2.5 pr-3 ${bodyTextClass(themeMode)}`}>{row.started_at ?? "—"}</td>
                          <td className={`py-2.5 ${bodyTextClass(themeMode)}`}>{formatDurationHours(row.duration_hours, locale)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className={`mt-4 rounded-2xl border px-4 py-4 text-sm ${themeMode === "dark" ? "border-white/8 bg-white/[0.03] text-white/72" : "border-slate-200 bg-slate-50 text-slate-600"}`}>{tx(locale, "noOpenDowntimes")}</div>
              )}
            </div>
          </section>
        </section>

        <section className="grid gap-2.5 xl:grid-cols-3">
          {hasPlannedActualData ? (
            <BoardChartCard
              title={tx(locale, "plannedVsActualHours")}
              subtitle={tx(locale, "scope")}
              themeMode={themeMode}
              height={300}
              categories={data.planned_vs_actual.map((item) => item.period)}
              categoryKeys={trailingDateKeys(dateEnd, data.planned_vs_actual.length)}
              onSelectCategory={focusCategory}
              series={[
                {
                  name: locale === "lv" ? "Reālās darba stundas" : "Actual work hours",
                  values: data.planned_vs_actual.map((item) => item.actual),
                  color: "#b8e6c3",
                  kind: "bar",
                },
                {
                  name: locale === "lv" ? "Plānotās dīkstāves" : "Planned downtime",
                  values: data.planned_vs_actual.map((item) => item.planned),
                  color: "#3182f6",
                  kind: "line",
                },
              ]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[300px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "plannedVsActualHours")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}

          {hasTaskDistributionData ? (
            <BoardChartCard
              title={tx(locale, "taskDistribution")}
              subtitle={tx(locale, "tasks")}
              themeMode={themeMode}
              height={300}
              categories={taskDistributionTrend.map((item) => item.period)}
              categoryKeys={taskDistributionTrend.map((item) => item.period)}
              onSelectCategory={focusCategory}
              series={[
                {
                  name: tx(locale, "regularShare"),
                  values: taskDistributionTrend.map((item) => item.regular),
                  color: "#32d1c6",
                  kind: "line",
                },
                {
                  name: tx(locale, "emergencyShare"),
                  values: taskDistributionTrend.map((item) => item.emergency),
                  color: "#ff6b77",
                  kind: "line",
                },
                {
                  name: tx(locale, "metricPlannedShare"),
                  values: taskDistributionTrend.map((item) => item.planned),
                  color: "#3b82f6",
                  kind: "line",
                },
              ]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[300px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "taskDistribution")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}

          {hasCostData ? (
            <BoardChartCard
              title={tx(locale, "costsLast12Months")}
              subtitle={tx(locale, "costs")}
              themeMode={themeMode}
              height={300}
              categories={costBreakdown.map((item) => item.period)}
              categoryKeys={costBreakdown.map((item) => item.period)}
              onSelectCategory={focusCategory}
              series={[
                {
                  name: tx(locale, "sparesCost"),
                  values: costBreakdown.map((item) => item.spares),
                  color: "#3b82f6",
                  kind: "bar",
                },
                {
                  name: tx(locale, "extraCost"),
                  values: costBreakdown.map((item) => item.extra),
                  color: "#94c5ff",
                  kind: "bar",
                },
              ]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[300px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "costsLast12Months")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}
        </section>

        <section className="grid gap-2.5 xl:grid-cols-3">
          {hasOverdueTrendData ? (
            <BoardChartCard
              title={tx(locale, "overdueTrend")}
              subtitle={tx(locale, "tasks")}
              themeMode={themeMode}
              height={250}
              categories={taskBoard.overdue_trend.map((item) => item.period)}
              categoryKeys={taskBoard.overdue_trend.map((item) => item.period)}
              onSelectCategory={focusCategory}
              series={[{
                name: tx(locale, "overdueTasks"),
                values: taskBoard.overdue_trend.map((item) => item.value),
                color: "#f97316",
                kind: "line",
              }]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[250px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "overdueTrend")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}

          {hasWorkHoursData ? (
            <BoardChartCard
              title={tx(locale, "workHoursLast12Months")}
              subtitle={tx(locale, "workReports")}
              themeMode={themeMode}
              height={250}
              categories={data.work_hours_12m.map((item) => item.period)}
              categoryKeys={data.work_hours_12m.map((item) => item.period)}
              onSelectCategory={focusCategory}
              series={[{
                name: locale === "lv" ? "Darba stundas" : "Work hours",
                values: data.work_hours_12m.map((item) => item.value),
                color: "#3182f6",
                kind: "bar",
              }]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[250px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "workHoursLast12Months")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}

          {hasMonthlyCostTotals ? (
            <BoardChartCard
              title={tx(locale, "monthlyCosts")}
              subtitle={tx(locale, "totalCost")}
              themeMode={themeMode}
              height={250}
              categories={costsBoard.monthly_total_costs.map((item) => item.period)}
              categoryKeys={costsBoard.monthly_total_costs.map((item) => item.period)}
              onSelectCategory={focusCategory}
              series={[{
                name: tx(locale, "totalCost"),
                values: costsBoard.monthly_total_costs.map((item) => item.value),
                color: "#0ea5e9",
                kind: "bar",
              }]}
            />
          ) : (
            <section className={panelClass(themeMode)}>
              <div className="flex h-[250px] flex-col justify-between px-5 py-5">
                <div className={eyebrowClass(themeMode)}>{tx(locale, "monthlyCosts")}</div>
                <div className={`grid flex-1 place-items-center text-sm ${bodyTextClass(themeMode)}`}>{tx(locale, "noChartData")}</div>
              </div>
            </section>
          )}
        </section>
      </div>
    </main>
  );
}
