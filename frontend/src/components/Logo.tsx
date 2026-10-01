export default function Logo({ size = 40 }: { size?: number }) {
  return (
    <div
      className="rounded-2xl flex items-center justify-center flex-shrink-0"
      style={{
        width: size,
        height: size,
        background: "#0f172a",
      }}
    >
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none">
        <path
          d="M12 2.5L4.5 5.5v5.5c0 5 3.2 8.9 7.5 10 4.3-1.1 7.5-5 7.5-10V5.5L12 2.5z"
          stroke="#22d3ee"
          strokeWidth="1.6"
          strokeLinejoin="round"
          fill="none"
        />
        <circle cx="12" cy="10" r="2.3" stroke="#22d3ee" strokeWidth="1.6" fill="none" />
        <circle cx="12" cy="10" r="0.9" fill="#22d3ee" />
        <line x1="10.3" y1="11.6" x2="8.8" y2="13.5" stroke="#22d3ee" strokeWidth="1.2" />
        <line x1="13.7" y1="11.6" x2="15.2" y2="13.5" stroke="#22d3ee" strokeWidth="1.2" />
        <circle cx="8.4" cy="14" r="1.3" fill="#f97316" />
        <circle cx="15.6" cy="14" r="1.3" fill="#f97316" />
      </svg>
    </div>
  )
}