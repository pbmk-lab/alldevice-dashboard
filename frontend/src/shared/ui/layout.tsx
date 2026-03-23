import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { NavLink, Outlet, useSearchParams } from "react-router-dom";

import { api } from "../api/client";
import { type Locale, tx } from "../i18n/translations";
import { DateRangePicker, getDateRangeTag } from "./date-range-picker";

const navItems = [
  { to: "/", key: "overview" as const },
  { to: "/triage", key: "triage" as const },
  { to: "/devices", key: "devices" as const },
  { to: "/work-reports", key: "workReports" as const },
  { to: "/data-quality", key: "dataQuality" as const },
  { to: "/admin", key: "admin" as const },
];

export function AppLayout() {
  const { data } = useQuery({ queryKey: ["filters-bootstrap"], queryFn: api.filters });
  const [searchParams, setSearchParams] = useSearchParams();
  const [lineQuery, setLineQuery] = useState("");
  const allLines = data?.lines ?? [];

  const locale = (searchParams.get("locale") as Locale | null) ?? data?.default_locale ?? "lv";
  const lineMode = searchParams.get("line_mode") ?? "all";
  const lines = searchParams.getAll("lines");
  const activeLines = lineMode === "none" ? [] : lineMode === "custom" ? lines : allLines;
  const filterLines = lineMode === "none" ? ["__no_line_selected__"] : activeLines;
  const dateStart = searchParams.get("date_start") ?? data?.default_start ?? "";
  const dateEnd = searchParams.get("date_end") ?? data?.default_end ?? "";
  const periodTag = data ? getDateRangeTag(locale, dateStart, dateEnd, data.min_date, data.max_date) : null;
  const lineSummary = lineMode === "all" ? `${allLines.length} / ${allLines.length}` : `${activeLines.length}`;
  const visibleLines = allLines.filter((line) => line.toLowerCase().includes(lineQuery.trim().toLowerCase()));

  const patchParams = (patch: Record<string, string | string[]>) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(patch).forEach(([key, value]) => {
      next.delete(key);
      if (Array.isArray(value)) value.forEach((item) => next.append(key, item));
      else next.set(key, value);
    });
    setSearchParams(next, { replace: true });
  };

  const toggleLine = (line: string) => {
    if (lineMode === "all") {
      patchParams({
        line_mode: "custom",
        lines: allLines.filter((item) => item !== line),
      });
      return;
    }

    const next = activeLines.includes(line)
      ? activeLines.filter((item) => item !== line)
      : [...activeLines, line];

    patchParams({
      line_mode: next.length ? "custom" : "none",
      lines: next,
    });
  };

  return (
    <div className="isolate grid min-h-screen lg:grid-cols-[310px_minmax(0,1fr)]">
      <aside data-theme="business" className="border-base-300/70 bg-base-100/95 text-base-content relative z-40 border-b backdrop-blur-xl lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="flex h-full flex-col gap-5 p-5">
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight">{tx(locale, "title")}</h1>
            <p className="text-base-content/60 max-w-[24ch] text-sm leading-6">{tx(locale, "subtitle")}</p>
          </div>

          <nav className="menu bg-base-200/40 rounded-box w-full gap-1 p-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={{ pathname: item.to, search: searchParams.toString() }}
                className={({ isActive }) =>
                  [
                    "rounded-box px-4 py-3 text-sm transition-colors",
                    isActive
                      ? "bg-primary text-primary-content shadow-sm"
                      : "text-base-content/70 hover:bg-base-300/70 hover:text-base-content",
                  ].join(" ")
                }
                end={item.to === "/"}
              >
                {tx(locale, item.key)}
              </NavLink>
            ))}
          </nav>

          <div className="space-y-4">
            <div className="text-base-content/60 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "filters")}</div>
            {data ? (
              <DateRangePicker
                locale={locale}
                start={dateStart}
                end={dateEnd}
                min={data.min_date}
                max={data.max_date}
                onChange={(nextStart, nextEnd) => patchParams({ date_start: nextStart, date_end: nextEnd })}
              />
            ) : (
              <div className="from-primary/12 via-base-100 to-warning/8 rounded-[1.2rem] border border-primary/18 bg-gradient-to-br p-4 shadow-sm">
                <strong className="block text-base font-semibold tracking-tight">{tx(locale, "dateRangeTitle")}</strong>
                <span className="text-base-content/65 mt-1 block text-sm">{tx(locale, "loading")}</span>
              </div>
            )}
          </div>

          <section className="bg-base-200/45 rounded-[1.4rem] border border-white/6 p-4">
            <div className="mb-3 flex items-end justify-between gap-3">
              <div>
                <div className="text-base-content/60 text-xs font-semibold uppercase tracking-[0.22em]">{tx(locale, "lines")}</div>
                <div className="mt-2 flex items-baseline gap-2">
                  <strong className="text-2xl font-semibold text-white">{activeLines.length}</strong>
                  <span className="text-base-content/60 text-sm">{tx(locale, "linesSelected")}</span>
                </div>
              </div>
              <span className="badge badge-outline badge-sm">{lineMode === "all" ? "ALL" : lineMode.toUpperCase()}</span>
            </div>

            <label className="input input-bordered bg-base-100/80 mb-3 flex items-center gap-2 rounded-full border-white/8">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="h-4 w-4 opacity-60" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m21 21-4.34-4.34" />
                <circle cx="11" cy="11" r="8" />
              </svg>
              <input
                type="text"
                value={lineQuery}
                onChange={(event) => setLineQuery(event.target.value)}
                className="grow"
                placeholder={tx(locale, "lineSearchPlaceholder")}
              />
            </label>

            <div className="mb-3 grid grid-cols-2 gap-2">
              <button type="button" className="btn btn-sm btn-primary" onClick={() => patchParams({ line_mode: "all", lines: [] })}>
                {tx(locale, "selectAll")}
              </button>
              <button type="button" className="btn btn-sm btn-ghost border border-white/8" onClick={() => patchParams({ line_mode: "none", lines: [] })}>
                {tx(locale, "clearAll")}
              </button>
            </div>

            <div className="max-h-72 space-y-2 overflow-auto pr-1">
              {visibleLines.map((line) => (
                <label
                  key={line}
                  className={[
                    "rounded-box flex cursor-pointer items-center gap-3 border px-3 py-2.5 transition-colors",
                    activeLines.includes(line)
                      ? "border-primary/40 bg-primary/12 text-white"
                      : "border-white/6 bg-base-100/55 text-base-content/76 hover:bg-base-100/80",
                  ].join(" ")}
                >
                  <input
                    type="checkbox"
                    className="checkbox checkbox-sm checkbox-primary"
                    checked={activeLines.includes(line)}
                    onChange={() => toggleLine(line)}
                  />
                  <span className="text-sm leading-5">{line}</span>
                </label>
              ))}
              {!visibleLines.length ? (
                <div className="rounded-box bg-base-100/60 text-base-content/60 border border-white/6 px-3 py-3 text-sm">
                  {tx(locale, "noMatchingLines")}
                </div>
              ) : null}
            </div>
          </section>

          <div className="mt-auto flex flex-col gap-3 rounded-[1.2rem] border border-white/6 bg-white/4 px-3 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <div className="text-base-content/55 text-[11px] font-semibold uppercase tracking-[0.22em]">{tx(locale, "periodLabel")}</div>
              {periodTag ? <div><span className="badge badge-sm badge-primary badge-soft">{periodTag}</span></div> : null}
              <div className="text-sm text-white">
                {dateStart || "—"} → {dateEnd || "—"}
              </div>
            </div>

            <div className="join">
              {(["lv", "en"] as const).map((item) => (
                <button
                  key={item}
                  className={`btn btn-sm join-item ${item === locale ? "btn-primary" : "btn-ghost"}`}
                  onClick={() => patchParams({ locale: item })}
                >
                  {item.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>
      </aside>

      <main data-theme="corporate" className="relative z-0 min-w-0 px-4 py-5 text-base-content sm:px-6 lg:px-8">
        <div className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="space-y-3">
            <div>
              <h2 className="text-base-content text-4xl font-semibold tracking-tight">{tx(locale, "title")}</h2>
              <p className="text-base-content/78 mt-2 max-w-2xl text-sm leading-6">{tx(locale, "subtitle")}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <div className="badge badge-lg badge-outline px-4 py-4">{tx(locale, "activeLines")}: {lineSummary}</div>
              {periodTag ? <div className="badge badge-lg badge-primary badge-soft px-4 py-4">{periodTag}</div> : null}
              <div className="badge badge-lg badge-outline px-4 py-4">
                {tx(locale, "periodLabel")}: {dateStart || "—"} → {dateEnd || "—"}
              </div>
            </div>
          </div>

          <div className="join self-start">
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
        </div>

        <Outlet
          context={{
            locale,
            filters: {
              locale,
              dateStart,
              dateEnd,
              lines: filterLines,
            },
            availableLines: allLines,
          }}
        />
      </main>
    </div>
  );
}
