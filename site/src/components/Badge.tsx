import { TONE_CLASSES, type Tone } from '../lib/labels'

export function Badge({ label, tone }: { label: string; tone: Tone }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${TONE_CLASSES[tone]}`}
    >
      {label}
    </span>
  )
}
