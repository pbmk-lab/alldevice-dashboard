type Props = {
  kind: "loading" | "error" | "empty";
  message: string;
};

export function PageState({ kind, message }: Props) {
  const tone =
    kind === "error"
      ? "alert-error"
      : kind === "loading"
        ? "alert-info"
        : "alert-warning";

  return (
    <div className="rounded-[1.6rem] border border-base-300/70 bg-base-100 p-5 shadow-sm">
      <div className={`alert ${tone}`}>
        <span>{message}</span>
      </div>
    </div>
  );
}
