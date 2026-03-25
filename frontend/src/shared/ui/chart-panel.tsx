import { useId, useMemo, useState } from "react";

type Series = {
  x: string[];
  y: number[];
  name: string;
  color: string;
  kind?: "scatter" | "bar";
  mode?: "lines+markers" | "lines";
  fill?: boolean;
  axis?: "y" | "y2";
};

type PieSeries = {
  labels: string[];
  values: number[];
  colors: string[];
};

type Props = {
  title: string;
  series: Series | PieSeries | Series[];
  type?: "scatter" | "bar" | "pie";
  subtitle?: string;
  height?: number;
  tone?: "default" | "spotlight";
  centerLabel?: string;
  themeMode?: "light" | "dark";
};

function panelFrameClass(isSpotlight: boolean, themeMode: "light" | "dark") {
  if (isSpotlight) {
    return themeMode === "dark"
      ? "card overflow-hidden border border-white/8 bg-[radial-gradient(circle_at_top_left,rgba(44,182,213,0.24),transparent_30%),radial-gradient(circle_at_85%_18%,rgba(255,71,139,0.12),transparent_22%),linear-gradient(180deg,#11131b_0%,#0b0d13_100%)] text-white shadow-[0_30px_70px_rgba(6,10,18,0.35)]"
      : "card overflow-hidden border border-slate-200/80 bg-[radial-gradient(circle_at_top_left,rgba(44,182,213,0.14),transparent_28%),radial-gradient(circle_at_85%_18%,rgba(255,176,0,0.12),transparent_24%),linear-gradient(180deg,#ffffff_0%,#f5f8fb_100%)] text-slate-900 shadow-[0_24px_60px_rgba(126,151,172,0.18)]";
  }

  return "card border-base-300/70 bg-base-100 shadow-sm";
}

function titleClass(isSpotlight: boolean, themeMode: "light" | "dark") {
  if (isSpotlight) {
    return themeMode === "dark"
      ? "text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-white/60"
      : "text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-slate-500";
  }

  return "text-base-content/72 text-xs font-semibold uppercase tracking-[0.22em]";
}

function subtitleClass(isSpotlight: boolean, themeMode: "light" | "dark") {
  if (isSpotlight) {
    return themeMode === "dark" ? "text-sm text-white/72" : "text-sm text-slate-600";
  }

  return "text-sm text-base-content/72";
}

function chartColors(isSpotlight: boolean, themeMode: "light" | "dark") {
  return {
    label: isSpotlight ? (themeMode === "dark" ? "rgba(255,255,255,0.72)" : "rgba(15,23,42,0.68)") : "rgba(15,23,42,0.62)",
    grid: isSpotlight
      ? themeMode === "dark"
        ? "rgba(255,255,255,0.08)"
        : "rgba(15,23,42,0.08)"
      : "rgba(15,23,42,0.08)",
    tooltipBg: themeMode === "dark" ? "rgba(2,6,23,0.9)" : "rgba(255,255,255,0.96)",
    tooltipBorder: themeMode === "dark" ? "rgba(255,255,255,0.12)" : "rgba(148,163,184,0.22)",
    tooltipText: themeMode === "dark" ? "#f8fafc" : "#0f172a",
    mutedText: themeMode === "dark" ? "rgba(255,255,255,0.7)" : "rgba(51,65,85,0.82)",
    track: themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.08)",
  };
}

function formatCompactValue(value: number) {
  if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(1)}k`;
  if (Math.abs(value) >= 100) return `${Math.round(value)}`;
  return `${Number(value.toFixed(1))}`;
}

function summaryPrefix(type: "scatter" | "bar" | "pie", isPie: boolean, hasMultipleSeries: boolean) {
  if (isPie) return "Total";
  if (type === "bar") return hasMultipleSeries ? "Latest" : "Last";
  return "Last";
}

function hexToRgba(value: string, alpha: number) {
  const clean = value.replace("#", "");
  if (clean.length !== 6) return value;
  const red = Number.parseInt(clean.slice(0, 2), 16);
  const green = Number.parseInt(clean.slice(2, 4), 16);
  const blue = Number.parseInt(clean.slice(4, 6), 16);
  return `rgba(${red},${green},${blue},${alpha})`;
}

function linePath(values: number[], width: number, height: number, offsetX: number, offsetY: number, min: number, max: number) {
  const range = max - min || 1;
  return values
    .map((value, index) => {
      const x = offsetX + (values.length === 1 ? width / 2 : (index / (values.length - 1)) * width);
      const y = offsetY + height - ((value - min) / range) * (height - 18) - 9;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

function polarPoint(cx: number, cy: number, r: number, angle: number) {
  return {
    x: cx + r * Math.cos(angle),
    y: cy + r * Math.sin(angle),
  };
}

function donutSegmentPath(cx: number, cy: number, radius: number, startAngle: number, endAngle: number) {
  const start = polarPoint(cx, cy, radius, startAngle);
  const end = polarPoint(cx, cy, radius, endAngle);
  const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
  return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
}

function PieChart({
  data,
  centerLabel,
  height,
  themeMode,
  isSpotlight,
}: {
  data: PieSeries;
  centerLabel?: string;
  height: number;
  themeMode: "light" | "dark";
  isSpotlight: boolean;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const gradientId = useId().replace(/:/g, "");
  const colors = chartColors(isSpotlight, themeMode);
  const total = data.values.reduce((sum, value) => sum + value, 0) || 1;
  const width = 760;
  const radius = 110;
  const centerX = 210;
  const centerY = height / 2;
  const gapAngle = data.values.filter((value) => value > 0).length > 1 ? 0.045 : 0;
  const drawable = 2 * Math.PI - gapAngle * data.values.filter((value) => value > 0).length;

  let offset = -Math.PI / 2;
  const slices = data.labels.map((label, index) => {
    const value = data.values[index] ?? 0;
    const rawAngle = total > 0 ? (value / total) * drawable : 0;
    const start = offset;
    const end = start + rawAngle;
    offset = end + (value > 0 ? gapAngle : 0);

    return {
      label,
      value,
      color: data.colors[index] ?? "#94a3b8",
      path: rawAngle > 0 ? donutSegmentPath(centerX, centerY, radius, start, end) : "",
      pct: total > 0 ? (value / total) * 100 : 0,
    };
  });

  const active = slices[hoveredIndex ?? 0] ?? null;
  const centerParts = centerLabel?.split("<br>") ?? [];
  const centerMain = centerParts[0]?.replace(/<[^>]+>/g, "") ?? "";
  const centerSub = centerParts[1]?.replace(/<[^>]+>/g, "") ?? "";

  return (
    <div className="space-y-4">
      <div className="relative">
        {active ? (
          <div
            className="absolute right-0 top-0 z-10 rounded-xl border px-3 py-2 text-xs shadow-sm"
            style={{
              background: colors.tooltipBg,
              borderColor: colors.tooltipBorder,
              color: colors.tooltipText,
            }}
          >
            <div className="flex items-center gap-2 font-semibold">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: active.color }} />
              <span>{active.label}</span>
            </div>
            <div className="mt-1" style={{ color: colors.mutedText }}>
              {active.value.toFixed(1)}h · {active.pct.toFixed(1)}%
            </div>
          </div>
        ) : null}

        <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ height: `${height}px` }}>
          <defs>
            <radialGradient id={`${gradientId}-pie-core`} cx="50%" cy="44%" r="72%">
              <stop offset="0%" stopColor={themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.98)"} />
              <stop offset="100%" stopColor={themeMode === "dark" ? "rgba(15,23,42,0.92)" : "rgba(248,250,252,0.96)"} />
            </radialGradient>
          </defs>
          <circle cx={centerX} cy={centerY} r={radius} fill="none" stroke={colors.track} strokeWidth="28" />
          {slices.map((slice, index) =>
            slice.path ? (
              <path
                key={slice.label}
                d={slice.path}
                fill="none"
                stroke={slice.color}
                strokeWidth={hoveredIndex === index ? 30 : 28}
                strokeLinecap="round"
                opacity={hoveredIndex === null || hoveredIndex === index ? 1 : 0.28}
                style={{ cursor: "pointer", transition: "opacity 180ms ease, stroke-width 180ms ease" }}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
            ) : null,
          )}

          <circle
            cx={centerX}
            cy={centerY}
            r="70"
            fill={`url(#${gradientId}-pie-core)`}
            stroke={themeMode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.06)"}
          />
          {centerMain ? (
            <text x={centerX} y={centerY - 6} textAnchor="middle" fontSize="26" fontWeight="600" fill={colors.tooltipText}>
              {centerMain}
            </text>
          ) : null}
          {centerSub ? (
            <text x={centerX} y={centerY + 18} textAnchor="middle" fontSize="12" fill={colors.mutedText}>
              {centerSub}
            </text>
          ) : null}

          {slices.map((slice, index) => {
            const legendX = 470;
            const legendY = 42 + index * 28;
            return (
              <g
                key={`${slice.label}-legend`}
                style={{ cursor: "pointer" }}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <circle cx={legendX} cy={legendY} r="6" fill={slice.color} />
                <text x={legendX + 16} y={legendY + 4} fontSize="13" fill={colors.tooltipText}>
                  {slice.label}
                </text>
                <text x={width - 16} y={legendY + 4} textAnchor="end" fontSize="13" fill={colors.mutedText}>
                  {slice.value.toFixed(1)}h
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

function CartesianChart({
  chartSeries,
  defaultType,
  height,
  themeMode,
  isSpotlight,
}: {
  chartSeries: Series[];
  defaultType: "scatter" | "bar";
  height: number;
  themeMode: "light" | "dark";
  isSpotlight: boolean;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const chartId = useId().replace(/:/g, "");
  const colors = chartColors(isSpotlight, themeMode);
  const width = 760;
  const chartHeight = Math.max(height - 46, 170);
  const paddingLeft = 50;
  const paddingRight = 18;
  const paddingTop = 10;
  const paddingBottom = 44;
  const plotWidth = width - paddingLeft - paddingRight;
  const plotHeight = chartHeight - paddingTop - paddingBottom;
  const categories = chartSeries[0]?.x ?? [];
  const allValues = chartSeries.flatMap((item) => item.y);
  const minValue = Math.min(...allValues, 0);
  const maxValue = Math.max(...allValues, 1);
  const range = maxValue - minValue || 1;
  const ticks = Array.from({ length: 4 }, (_, index) => minValue + (range / 3) * index);
  const xStep = categories.length > 1 ? plotWidth / (categories.length - 1) : plotWidth / 2;
  const barSeries = chartSeries.filter((item) => (item.kind ?? defaultType) === "bar");
  const barClusterWidth = Math.min(34, plotWidth / Math.max(categories.length, 1) / 1.5);
  const barWidth = Math.max(barClusterWidth / Math.max(barSeries.length, 1) - 3, 7);

  const xForIndex = (index: number) => paddingLeft + (categories.length === 1 ? plotWidth / 2 : xStep * index);
  const yForValue = (value: number) => paddingTop + ((maxValue - value) / range) * plotHeight;
  const baselineY = yForValue(0);

  return (
    <div className="space-y-4">
      <div className="relative">
        {hoveredIndex !== null ? (
          <div
            className="absolute right-0 top-0 z-10 rounded-xl border px-3 py-2 text-xs shadow-sm"
            style={{
              background: colors.tooltipBg,
              borderColor: colors.tooltipBorder,
              color: colors.tooltipText,
            }}
          >
            <div className="font-semibold">{categories[hoveredIndex]}</div>
            <div className="mt-1 space-y-1">
              {chartSeries.map((item) => (
                <div key={`${item.name}-${categories[hoveredIndex]}`} className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span style={{ color: colors.mutedText }}>
                    {item.name}: {Number(item.y[hoveredIndex] ?? 0).toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <svg viewBox={`0 0 ${width} ${chartHeight}`} className="w-full" style={{ height: `${height}px` }}>
          <defs>
            {chartSeries.map((item, index) => (
              <linearGradient
                key={`${item.name}-${index}-gradient`}
                id={`${chartId}-series-${index}`}
                x1="0"
                x2="0"
                y1="0"
                y2="1"
              >
                <stop offset="0%" stopColor={hexToRgba(item.color, defaultType === "bar" || item.kind === "bar" ? 0.95 : 0.3)} />
                <stop offset="100%" stopColor={hexToRgba(item.color, defaultType === "bar" || item.kind === "bar" ? 0.58 : 0.04)} />
              </linearGradient>
            ))}
          </defs>
          {ticks.map((tick) => {
            const y = yForValue(tick);
            return (
              <g key={tick}>
                <line x1={paddingLeft} x2={width - paddingRight} y1={y} y2={y} stroke={colors.grid} strokeWidth="1" />
                <text x={paddingLeft - 8} y={y + 4} textAnchor="end" fontSize="11" fill={colors.label}>
                  {formatCompactValue(tick)}
                </text>
              </g>
            );
          })}

          {hoveredIndex !== null ? (
            <line
              x1={xForIndex(hoveredIndex)}
              x2={xForIndex(hoveredIndex)}
              y1={paddingTop}
              y2={paddingTop + plotHeight}
              stroke={themeMode === "dark" ? "rgba(255,255,255,0.18)" : "rgba(15,23,42,0.18)"}
              strokeWidth="1"
              strokeDasharray="4 4"
            />
          ) : null}

          {chartSeries.map((item) => {
            const kind = item.kind ?? defaultType;

            if (kind === "bar") {
              const barIndex = barSeries.findIndex((entry) => entry.name === item.name && entry.color === item.color);
              return item.y.map((value, index) => {
                const centerX = xForIndex(index);
                const x = centerX - barClusterWidth / 2 + barIndex * (barWidth + 3);
                const y = Math.min(yForValue(value), baselineY);
                const barHeight = Math.abs(baselineY - yForValue(value));
                return (
                  <rect
                    key={`${item.name}-${index}`}
                    x={x}
                    y={y}
                    width={barWidth}
                    height={Math.max(barHeight, 1)}
                    rx="3"
                    fill={`url(#${chartId}-series-${barIndex})`}
                    opacity={hoveredIndex === null || hoveredIndex === index ? 0.98 : 0.6}
                  />
                );
              });
            }

            const path = linePath(item.y, plotWidth, plotHeight, paddingLeft, paddingTop, minValue, maxValue);
            return (
              <g key={item.name}>
                {item.fill || chartSeries.length === 1 ? (
                  <path
                    d={`${path} L ${paddingLeft + plotWidth} ${baselineY} L ${paddingLeft} ${baselineY} Z`}
                    fill={`url(#${chartId}-series-${chartSeries.findIndex((entry) => entry.name === item.name && entry.color === item.color)})`}
                    stroke="none"
                  />
                ) : null}
                <path d={path} fill="none" stroke={item.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                {item.y.map((value, index) => (
                  <circle
                    key={`${item.name}-${index}`}
                    cx={xForIndex(index)}
                    cy={yForValue(value)}
                    r={hoveredIndex === index ? 4.8 : 3}
                    fill={item.color}
                    stroke={hoveredIndex === index ? (themeMode === "dark" ? "#ffffff" : "#0f172a") : "none"}
                    strokeWidth={hoveredIndex === index ? 1.4 : 0}
                  />
                ))}
              </g>
            );
          })}

          {categories.map((category, index) => {
            const currentX = xForIndex(index);
            const previousX = index > 0 ? xForIndex(index - 1) : paddingLeft;
            const nextX = index < categories.length - 1 ? xForIndex(index + 1) : width - paddingRight;
            const zoneWidth = categories.length === 1 ? plotWidth : nextX - previousX;
            const zoneX = categories.length === 1 ? paddingLeft : currentX - zoneWidth / 2;
            return (
              <g key={`${category}-${index}`}>
                <rect
                  x={zoneX}
                  y={paddingTop}
                  width={Math.max(zoneWidth, 18)}
                  height={plotHeight}
                  fill="transparent"
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                />
                <text
                  x={currentX}
                  y={chartHeight - 10}
                  textAnchor="end"
                  transform={`rotate(-38 ${currentX} ${chartHeight - 10})`}
                  fontSize="11"
                  fill={colors.label}
                >
                  {category}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {chartSeries.length > 1 ? (
        <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs">
          {chartSeries.map((item) => (
            <div key={item.name} className="flex items-center gap-2" style={{ color: colors.mutedText }}>
              <span className="rounded-full border px-2.5 py-1" style={{ borderColor: colors.grid }}>
                <span className="mr-2 inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
              </span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function ChartPanel({
  title,
  series,
  type = "scatter",
  subtitle,
  height = 280,
  tone = "default",
  centerLabel,
  themeMode = "light",
}: Props) {
  const isSpotlight = tone === "spotlight";
  const frameClass = panelFrameClass(isSpotlight, themeMode);
  const seriesArray = useMemo(
    () => (Array.isArray(series) ? series : "labels" in series ? null : [series]),
    [series],
  );
  const isPie = "labels" in (series as PieSeries) && type === "pie";
  const summaryLabel =
    isPie
      ? formatCompactValue((series as PieSeries).values.reduce((sum, value) => sum + value, 0))
      : seriesArray?.[0]?.y.length
        ? formatCompactValue(seriesArray[0].y.at(-1) ?? 0)
        : null;

  return (
    <section className={frameClass}>
      <div className="card-body gap-4">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className={titleClass(isSpotlight, themeMode)}>{title}</div>
            {subtitle ? <div className={subtitleClass(isSpotlight, themeMode)}>{subtitle}</div> : null}
          </div>
          {summaryLabel ? (
            <div
              className="rounded-full border px-3 py-1 text-xs font-semibold"
              style={{
                borderColor: chartColors(isSpotlight, themeMode).grid,
                color: chartColors(isSpotlight, themeMode).mutedText,
              }}
            >
              {summaryPrefix(type, isPie, Boolean(seriesArray && seriesArray.length > 1))} {summaryLabel}
            </div>
          ) : null}
        </div>

        {isPie ? (
          <PieChart data={series as PieSeries} centerLabel={centerLabel} height={height} themeMode={themeMode} isSpotlight={isSpotlight} />
        ) : seriesArray?.length ? (
          <CartesianChart
            chartSeries={seriesArray}
            defaultType={type === "bar" ? "bar" : "scatter"}
            height={height}
            themeMode={themeMode}
            isSpotlight={isSpotlight}
          />
        ) : (
          <div className="grid place-items-center rounded-2xl bg-base-200 text-sm text-base-content/72" style={{ height: `${height}px` }}>
            No chart data
          </div>
        )}
      </div>
    </section>
  );
}
