type Props = {
  mode: "light" | "dark";
  onChange: (mode: "light" | "dark") => void;
  compact?: boolean;
};

export function ThemeToggle({ mode, onChange, compact = false }: Props) {
  const dark = mode === "dark";
  const sizeClass = compact ? "h-9 w-9" : "h-10 w-10";
  const ringClass = dark
    ? "border-cyan-200/18 bg-slate-900/80 text-slate-50"
    : "border-amber-200/80 bg-amber-50 text-amber-500";

  return (
    <button
      type="button"
      onClick={() => onChange(dark ? "light" : "dark")}
      aria-label={`Switch to ${dark ? "light" : "dark"} theme`}
      title={`Switch to ${dark ? "light" : "dark"} theme`}
      aria-pressed={dark}
      className={[
        "group relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full border transition-all duration-400 ease-out",
        "focus:outline-none focus:ring-2 focus:ring-primary/35 focus:ring-offset-2",
        "hover:border-primary/40 active:scale-[0.98]",
        sizeClass,
        ringClass,
      ].join(" ")}
    >
      <span
        className={[
          "absolute inset-0 rounded-full transition-opacity duration-500",
          dark ? "opacity-100" : "opacity-0",
        ].join(" ")}
      >
        <span className="absolute left-2 top-2 h-1 w-1 rounded-full bg-white/75" />
        <span className="absolute right-2.5 top-3 h-0.5 w-0.5 rounded-full bg-white/65" />
        <span className="absolute right-4 bottom-2.5 h-1 w-1 rounded-full bg-cyan-100/65" />
      </span>

      <span
        className={[
          "pointer-events-none absolute inset-1 rounded-full transition-opacity duration-500",
          dark ? "opacity-0" : "bg-white/45 opacity-100",
        ].join(" ")}
      />

      <span className="relative block h-5 w-5">
        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
          className={[
            "absolute inset-0 h-5 w-5 transition-all duration-500 ease-out",
            dark ? "scale-[0.65] rotate-90 opacity-0" : "scale-100 rotate-0 opacity-100",
          ].join(" ")}
        >
          <circle cx="12" cy="12" r="4.4" fill="currentColor" />
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <line
              key={deg}
              x1="12"
              y1="1.75"
              x2="12"
              y2="5"
              stroke="currentColor"
              strokeWidth="1.9"
              strokeLinecap="round"
              transform={`rotate(${deg} 12 12)`}
            />
          ))}
        </svg>

        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
          className={[
            "absolute inset-0 h-5 w-5 transition-all duration-500 ease-out",
            dark ? "scale-100 rotate-0 opacity-100" : "scale-[0.65] -rotate-90 opacity-0",
          ].join(" ")}
        >
          <defs>
            <mask id={`theme-toggle-moon-${compact ? "compact" : "default"}`}>
              <rect width="24" height="24" fill="white" />
              <circle cx="15.2" cy="8.8" r="6.3" fill="black" />
            </mask>
          </defs>
          <circle cx="11.4" cy="12.4" r="7.2" fill="currentColor" mask={`url(#theme-toggle-moon-${compact ? "compact" : "default"})`} />
        </svg>
      </span>
    </button>
  );
}
