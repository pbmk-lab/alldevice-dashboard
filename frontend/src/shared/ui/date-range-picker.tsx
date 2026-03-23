import { useEffect, useRef, useState } from "react";

import { type Locale, tx } from "../i18n/translations";

type DateField = "start" | "end";

type Props = {
  locale: Locale;
  start: string;
  end: string;
  min: string;
  max: string;
  onChange: (start: string, end: string) => void;
};

type CalendarDay = {
  iso: string;
  label: number;
  disabled: boolean;
  currentMonth: boolean;
};

const weekLabels: Record<Locale, string[]> = {
  lv: ["Pr", "Ot", "Tr", "Ce", "Pk", "Se", "Sv"],
  en: ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
};

function parseIsoDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day, 12, 0, 0, 0);
}

function toIsoDate(date: Date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(date: Date, value: number) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + value, 12, 0, 0, 0);
}

function clampIso(value: string, min: string, max: string) {
  if (value < min) return min;
  if (value > max) return max;
  return value;
}

function addMonths(date: Date, value: number) {
  return new Date(date.getFullYear(), date.getMonth() + value, 1, 12, 0, 0, 0);
}

function startOfMonth(value: string) {
  const date = parseIsoDate(value);
  return new Date(date.getFullYear(), date.getMonth(), 1, 12, 0, 0, 0);
}

function formatMonth(locale: Locale, value: Date) {
  return new Intl.DateTimeFormat(locale === "lv" ? "lv-LV" : "en-US", {
    month: "long",
    year: "numeric",
  }).format(value);
}

function formatDisplayDate(locale: Locale, value: string) {
  return new Intl.DateTimeFormat(locale === "lv" ? "lv-LV" : "en-US", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(parseIsoDate(value));
}

function buildCalendarDays(month: Date, min: string, max: string) {
  const firstDay = new Date(month.getFullYear(), month.getMonth(), 1, 12, 0, 0, 0);
  const gridStart = new Date(firstDay);
  const offset = (firstDay.getDay() + 6) % 7;
  gridStart.setDate(firstDay.getDate() - offset);

  const days: CalendarDay[] = [];

  for (let index = 0; index < 42; index += 1) {
    const current = new Date(gridStart);
    current.setDate(gridStart.getDate() + index);
    const iso = toIsoDate(current);
    days.push({
      iso,
      label: current.getDate(),
      disabled: iso < min || iso > max,
      currentMonth: current.getMonth() === month.getMonth(),
    });
  }

  return days;
}

function clampRange(start: string, end: string, min: string, max: string) {
  const nextStart = start < min ? min : start > max ? max : start;
  const nextEnd = end < min ? min : end > max ? max : end;

  if (nextStart <= nextEnd) return { start: nextStart, end: nextEnd };
  return { start: nextEnd, end: nextStart };
}

export function getDateRangeTag(locale: Locale, start: string, end: string, min: string, max: string) {
  if (!start || !end || !min || !max) return null;

  const today = clampIso(toIsoDate(new Date()), min, max);
  const yesterday = clampIso(toIsoDate(addDays(parseIsoDate(today), -1)), min, max);
  const trailing30Start = clampIso(toIsoDate(addDays(parseIsoDate(today), -29)), min, max);
  const trailing90Start = clampIso(toIsoDate(addDays(parseIsoDate(today), -89)), min, max);
  const yearStart = clampIso(`${today.slice(0, 4)}-01-01`, min, max);

  if (start === today && end === today) return tx(locale, "rangeTagToday");
  if (start === yesterday && end === yesterday) return tx(locale, "rangeTagYesterday");
  if (start === trailing30Start && end === today) return tx(locale, "rangeTag30d");
  if (start === trailing90Start && end === today) return tx(locale, "rangeTag90d");
  if (start === yearStart && end === today) return tx(locale, "rangeTagYtd");
  if (start === min && end === max) return tx(locale, "rangeTagFull");

  return tx(locale, "rangeTagCustom");
}

export function DateRangePicker({ locale, start, end, min, max, onChange }: Props) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [activeField, setActiveField] = useState<DateField>("start");
  const [visibleMonth, setVisibleMonth] = useState(() => startOfMonth(start || min));
  const [draftStart, setDraftStart] = useState(start || min);
  const [draftEnd, setDraftEnd] = useState(end || max);
  const [hoverDate, setHoverDate] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setDraftStart(start || min);
      setDraftEnd(end || max);
      setHoverDate(null);
    }
  }, [start, end, min, max, isOpen]);

  useEffect(() => {
    if (!isOpen) return undefined;

    const handlePointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setIsOpen(false);
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen]);

  const syncRange = (nextStart: string, nextEnd: string) => {
    const normalized = clampRange(nextStart, nextEnd, min, max);
    onChange(normalized.start, normalized.end);
  };

  const openPicker = () => {
    setDraftStart(start || min);
    setDraftEnd(end || max);
    setActiveField("start");
    setVisibleMonth(startOfMonth(start || min));
    setHoverDate(null);
    setIsOpen((current) => !current);
  };

  const handlePreset = (kind: "today" | "yesterday" | "30d" | "90d" | "ytd" | "full") => {
    const today = clampIso(toIsoDate(new Date()), min, max);
    const todayDate = parseIsoDate(today);
    const presetStart =
      kind === "today"
        ? today
        : kind === "yesterday"
          ? clampIso(toIsoDate(addDays(todayDate, -1)), min, max)
        : kind === "30d"
          ? clampIso(toIsoDate(addDays(todayDate, -29)), min, max)
        : kind === "90d"
          ? clampIso(toIsoDate(addDays(todayDate, -89)), min, max)
          : kind === "ytd"
            ? clampIso(`${today.slice(0, 4)}-01-01`, min, max)
            : min;

    const nextStart = presetStart < min ? min : presetStart;
    const nextEnd = kind === "full" ? max : kind === "yesterday" ? nextStart : today;
    setDraftStart(nextStart);
    setDraftEnd(nextEnd);
    setHoverDate(null);
    syncRange(nextStart, nextEnd);
    setVisibleMonth(startOfMonth(nextStart));
    setActiveField("start");
    setIsOpen(false);
  };

  const handleDatePick = (value: string) => {
    if (activeField === "start") {
      setDraftStart(value);
      setDraftEnd(value);
      setHoverDate(null);
      setActiveField("end");
      setVisibleMonth(startOfMonth(value));
      return;
    }

    const nextStart = !draftStart || value < draftStart ? value : draftStart;
    setDraftStart(nextStart);
    setDraftEnd(value);
    setHoverDate(null);
    syncRange(nextStart, value);
    setIsOpen(false);
  };

  const firstMonthDays = buildCalendarDays(visibleMonth, min, max);
  const secondMonth = addMonths(visibleMonth, 1);
  const secondMonthDays = buildCalendarDays(secondMonth, min, max);
  const activeTag = getDateRangeTag(locale, start, end, min, max);
  const previewEnd = activeField === "end" && hoverDate ? hoverDate : draftEnd;
  const previewStart = draftStart || start || min;
  const previewRange = clampRange(previewStart, previewEnd || previewStart, min, max);
  const draftLabelStart = previewRange.start;
  const draftLabelEnd = previewRange.end;

  return (
    <div className="relative" ref={rootRef}>
      <div className="text-base-content/60 mb-1 text-xs font-semibold uppercase tracking-[0.22em]">
        {tx(locale, "periodLabel")}
      </div>

      <button
        type="button"
        className={[
          "from-primary/12 via-base-100 to-warning/8 w-full rounded-[1.2rem] border bg-gradient-to-br p-4 text-left shadow-sm transition",
          isOpen ? "border-warning/30 -translate-y-0.5" : "border-primary/18 hover:border-warning/20 hover:-translate-y-0.5",
        ].join(" ")}
        onClick={openPicker}
      >
        <div className="space-y-1">
          <strong className="block text-base font-semibold tracking-tight">{tx(locale, "dateRangeTitle")}</strong>
          {activeTag ? (
            <div className="mt-2">
              <span className="badge badge-sm badge-primary badge-soft">{activeTag}</span>
            </div>
          ) : null}
          <span className="text-base-content/65 block text-sm">
            {formatDisplayDate(locale, start)} - {formatDisplayDate(locale, end)}
          </span>
        </div>
        <span className="text-base-content/55 mt-3 inline-flex text-xs">{tx(locale, "dateRangeHint")}</span>
      </button>

      {isOpen ? (
        <div className="bg-base-100 absolute left-0 top-[calc(100%+12px)] z-[80] w-[min(680px,calc(100vw-40px))] rounded-[1.6rem] border border-white/8 p-4 shadow-2xl backdrop-blur-xl">
          <div className="grid gap-3 md:grid-cols-2">
            <button
              type="button"
              className={`rounded-2xl border p-3 text-left ${activeField === "start" ? "border-primary/30 bg-primary/10" : "border-white/8 bg-base-200/30"}`}
              onClick={() => setActiveField("start")}
            >
              <span className="text-base-content/55 text-xs font-semibold uppercase tracking-[0.18em]">{tx(locale, "periodStart")}</span>
              <strong className="mt-2 block text-sm">{formatDisplayDate(locale, draftLabelStart)}</strong>
            </button>
            <button
              type="button"
              className={`rounded-2xl border p-3 text-left ${activeField === "end" ? "border-primary/30 bg-primary/10" : "border-white/8 bg-base-200/30"}`}
              onClick={() => setActiveField("end")}
            >
              <span className="text-base-content/55 text-xs font-semibold uppercase tracking-[0.18em]">{tx(locale, "periodEnd")}</span>
              <strong className="mt-2 block text-sm">{formatDisplayDate(locale, draftLabelEnd)}</strong>
            </button>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => handlePreset("today")}>
              {tx(locale, "presetToday")}
            </button>
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => handlePreset("yesterday")}>
              {tx(locale, "presetYesterday")}
            </button>
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => handlePreset("30d")}>
              {tx(locale, "preset30d")}
            </button>
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => handlePreset("90d")}>
              {tx(locale, "preset90d")}
            </button>
            <button type="button" className="btn btn-sm btn-ghost" onClick={() => handlePreset("ytd")}>
              {tx(locale, "presetYtd")}
            </button>
            <button type="button" className="btn btn-sm btn-primary" onClick={() => handlePreset("full")}>
              {tx(locale, "presetFull")}
            </button>
          </div>

          <div className="mt-4 flex items-center justify-between gap-2">
            <button type="button" className="btn btn-sm btn-outline" onClick={() => setVisibleMonth((current) => addMonths(current, -1))}>
              {tx(locale, "calendarPrev")}
            </button>
            <button type="button" className="btn btn-sm btn-outline" onClick={() => setVisibleMonth((current) => addMonths(current, 1))}>
              {tx(locale, "calendarNext")}
            </button>
          </div>

          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            {[
              { label: formatMonth(locale, visibleMonth), days: firstMonthDays },
              { label: formatMonth(locale, secondMonth), days: secondMonthDays },
            ].map((calendar) => (
              <div key={calendar.label} className="bg-base-200/35 rounded-[1.2rem] border border-white/6 p-3">
                <div className="text-base-content/55 mb-3 text-xs font-semibold uppercase tracking-[0.18em]">{calendar.label}</div>
                <div className="text-base-content/50 mb-2 grid grid-cols-7 gap-1 text-center text-[11px] font-semibold uppercase tracking-[0.18em]">
                  {weekLabels[locale].map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {calendar.days.map((day) => {
                    const inRange = day.iso >= draftLabelStart && day.iso <= draftLabelEnd;
                    const isEdge = day.iso === draftLabelStart || day.iso === draftLabelEnd;
                    return (
                      <button
                        key={day.iso}
                        type="button"
                        disabled={day.disabled}
                        className={[
                          "aspect-square rounded-xl border text-sm transition",
                          day.currentMonth ? "text-base-content" : "text-base-content/30",
                          inRange ? "border-primary/20 bg-primary/12 text-base-content" : "border-transparent hover:bg-primary/10",
                          isEdge ? "border-primary bg-primary text-primary-content font-semibold shadow-sm hover:bg-primary" : "",
                          day.disabled ? "cursor-not-allowed opacity-25" : "",
                        ].join(" ")}
                        onMouseEnter={() => {
                          if (activeField === "end" && !day.disabled) setHoverDate(day.iso);
                        }}
                        onClick={() => handleDatePick(day.iso)}
                      >
                        {day.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex flex-col gap-2 border-t border-white/6 pt-4 text-sm md:flex-row md:items-end md:justify-between">
            <span className="text-base-content/58">{tx(locale, activeField === "start" ? "pickStartHint" : "pickEndHint")}</span>
            <strong>
              {formatDisplayDate(locale, draftLabelStart)} - {formatDisplayDate(locale, draftLabelEnd)}
            </strong>
          </div>
        </div>
      ) : null}
    </div>
  );
}
