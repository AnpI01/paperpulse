import clsx from 'clsx'
import { subfieldStyle } from '../utils/subfieldColor.js'

function ScoreBadge({ score }) {
  if (score == null) return null
  const cls =
    score >= 8
      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
      : score >= 6
        ? 'bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300'
        : score >= 4
          ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
          : 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300'
  return (
    <span className={clsx('text-xs font-semibold px-2 py-0.5 rounded-full tabular-nums', cls)}>
      {score.toFixed(1)}
    </span>
  )
}

function SourceBadge({ source }) {
  return (
    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 font-medium">
      {source === 'arxiv' ? 'arXiv' : 'S2'}
    </span>
  )
}

export default function PaperCard({ paper, onClick }) {
  const { color, bg } = subfieldStyle(paper.subfield)

  const formattedDate = paper.published_at
    ? new Date(paper.published_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  const authorDisplay =
    paper.authors?.length > 3
      ? paper.authors.slice(0, 3).join(', ') + ' et al.'
      : (paper.authors ?? []).join(', ')

  return (
    <article
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}
      className={clsx(
        'relative flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800',
        'cursor-pointer select-none overflow-hidden',
        'hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-500',
        'transition-all duration-150',
      )}
    >
      {/* Left accent bar */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
        style={{ backgroundColor: color }}
      />

      <div className="pl-4 pr-4 pt-4 pb-3 flex flex-col gap-2.5 flex-1 ml-0.5">
        {/* Top row: subfield + score */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          {paper.subfield ? (
            <span
              className="text-xs font-medium px-2 py-0.5 rounded-full"
              style={{ color, backgroundColor: bg }}
            >
              {paper.subfield}
            </span>
          ) : (
            <span className="text-xs text-slate-400 italic">Unclassified</span>
          )}
          <ScoreBadge score={paper.impact_score} />
        </div>

        {/* Title */}
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 line-clamp-2 leading-snug">
          {paper.title}
        </h3>

        {/* Authors */}
        {authorDisplay && (
          <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{authorDisplay}</p>
        )}

        {/* Key takeaway */}
        {paper.key_takeaway && (
          <p className="text-xs text-slate-600 dark:text-slate-400 italic line-clamp-2 leading-relaxed">
            "{paper.key_takeaway}"
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5">
            <SourceBadge source={paper.source} />
            {formattedDate && (
              <span className="text-xs text-slate-400">{formattedDate}</span>
            )}
          </div>
          <span className="text-xs text-indigo-500 dark:text-indigo-400 font-medium">
            View details →
          </span>
        </div>
      </div>
    </article>
  )
}
