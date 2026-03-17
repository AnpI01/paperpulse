import { useEffect, useState } from 'react'
import { X, ExternalLink, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'
import { subfieldStyle } from '../utils/subfieldColor.js'

function ScorePill({ score }) {
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
    <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', cls)}>
      Score: {score.toFixed(1)} / 10
    </span>
  )
}

function Section({ title, children }) {
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        {title}
      </h4>
      {children}
    </div>
  )
}

export default function PaperModal({ paper, onClose }) {
  const [abstractExpanded, setAbstractExpanded] = useState(false)
  const { color, bg } = subfieldStyle(paper.subfield)

  // Lock body scroll and handle Escape
  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKey = e => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = prev
      window.removeEventListener('keydown', onKey)
    }
  }, [onClose])

  const formattedDate = paper.published_at
    ? new Date(paper.published_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  const isLongAbstract = paper.abstract?.length > 400

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div
        className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh]
          overflow-y-auto border border-slate-200 dark:border-slate-700"
      >
        {/* Top accent bar */}
        <div className="h-1 rounded-t-2xl w-full" style={{ backgroundColor: color }} />

        <div className="p-6 space-y-5">
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 leading-snug flex-1">
              {paper.title}
            </h2>
            <button
              onClick={onClose}
              className="flex-shrink-0 p-1.5 rounded-lg text-slate-400 hover:text-slate-600
                dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Close"
            >
              <X size={18} />
            </button>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2">
            {paper.subfield && (
              <span
                className="text-xs font-medium px-2.5 py-1 rounded-full"
                style={{ color, backgroundColor: bg }}
              >
                {paper.subfield}
              </span>
            )}
            <ScorePill score={paper.impact_score} />
            <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-medium">
              {paper.source === 'arxiv' ? 'arXiv' : 'Semantic Scholar'}
            </span>
            {formattedDate && (
              <span className="text-xs text-slate-400 dark:text-slate-500">{formattedDate}</span>
            )}
          </div>

          {/* Authors */}
          {paper.authors?.length > 0 && (
            <Section title="Authors">
              <p className="text-sm text-slate-700 dark:text-slate-300">
                {paper.authors.join(', ')}
              </p>
            </Section>
          )}

          {/* Key takeaway */}
          {paper.key_takeaway && (
            <Section title="Key Takeaway">
              <p className="text-sm text-slate-700 dark:text-slate-300 italic leading-relaxed border-l-2 pl-3"
                style={{ borderColor: color }}>
                {paper.key_takeaway}
              </p>
            </Section>
          )}

          {/* AI Summary */}
          {paper.summary && (
            <Section title="AI Summary">
              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {paper.summary}
              </p>
            </Section>
          )}

          {/* Abstract */}
          {paper.abstract && (
            <Section title="Abstract">
              <div>
                <p
                  className={clsx(
                    'text-sm text-slate-600 dark:text-slate-400 leading-relaxed',
                    !abstractExpanded && isLongAbstract && 'line-clamp-3',
                  )}
                >
                  {paper.abstract}
                </p>
                {isLongAbstract && (
                  <button
                    onClick={() => setAbstractExpanded(v => !v)}
                    className="mt-1 flex items-center gap-1 text-xs text-indigo-500 dark:text-indigo-400 hover:underline"
                  >
                    {abstractExpanded ? (
                      <><ChevronUp size={12} /> Show less</>
                    ) : (
                      <><ChevronDown size={12} /> Show more</>
                    )}
                  </button>
                )}
              </div>
            </Section>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            {paper.url && (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
                  bg-indigo-600 hover:bg-indigo-700 text-white transition-colors"
              >
                <ExternalLink size={14} />
                Open Paper
              </a>
            )}
            {paper.pdf_url && (
              <a
                href={paper.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
                  border border-slate-200 dark:border-slate-700
                  text-slate-700 dark:text-slate-300
                  hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                <BookOpen size={14} />
                View PDF
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
