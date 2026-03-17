import { useQuery } from '@tanstack/react-query'
import { SlidersHorizontal, X } from 'lucide-react'
import clsx from 'clsx'
import { fetchStats } from '../api/client.js'
import { subfieldStyle } from '../utils/subfieldColor.js'

const EMPTY_FILTERS = { subfield: null, dateFrom: '', dateTo: '', minScore: 0 }

function hasActiveFilters(filters) {
  return filters.subfield || filters.dateFrom || filters.dateTo || filters.minScore > 0
}

export default function FilterSidebar({ filters, onFiltersChange, isOpen, onClose }) {
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: fetchStats })
  const subfields = Object.entries(stats?.papers_by_subfield ?? {}).sort((a, b) => b[1] - a[1])

  function set(key, value) {
    onFiltersChange({ ...filters, [key]: value })
  }

  function clearAll() {
    onFiltersChange(EMPTY_FILTERS)
  }

  const sidebar = (
    <aside className="flex flex-col gap-5 w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
          <SlidersHorizontal size={15} />
          Filters
          {hasActiveFilters(filters) && (
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 text-xs font-medium">
              active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasActiveFilters(filters) && (
            <button
              onClick={clearAll}
              className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 underline"
            >
              Clear all
            </button>
          )}
          {/* Mobile close */}
          <button
            onClick={onClose}
            className="md:hidden text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 p-1"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Subfield */}
      <section>
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
          Subfield
        </p>
        <div className="flex flex-col gap-1">
          {subfields.length === 0 && (
            <p className="text-xs text-slate-400 italic">No data yet</p>
          )}
          {subfields.map(([sf, count]) => {
            const { color, bg } = subfieldStyle(sf)
            const active = filters.subfield === sf
            return (
              <button
                key={sf}
                onClick={() => set('subfield', active ? null : sf)}
                className={clsx(
                  'flex items-center justify-between w-full px-2.5 py-1.5 rounded-lg text-sm text-left',
                  'border transition-all',
                  active
                    ? 'border-transparent font-medium'
                    : 'border-transparent hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300',
                )}
                style={active ? { backgroundColor: bg, color, borderColor: color } : {}}
              >
                <span className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  {sf}
                </span>
                <span className="text-xs text-slate-400 dark:text-slate-500 tabular-nums">{count}</span>
              </button>
            )
          })}
        </div>
      </section>

      {/* Date range */}
      <section>
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
          Date Range
        </p>
        <div className="flex flex-col gap-2">
          <div>
            <label className="text-xs text-slate-500 dark:text-slate-400 mb-1 block">From</label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={e => set('dateFrom', e.target.value)}
              className="w-full text-sm px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700
                bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-500 dark:text-slate-400 mb-1 block">To</label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={e => set('dateTo', e.target.value)}
              className="w-full text-sm px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700
                bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </section>

      {/* Min score */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Min Impact Score
          </p>
          <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 tabular-nums">
            {filters.minScore.toFixed(1)}
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={10}
          step={0.5}
          value={filters.minScore}
          onChange={e => set('minScore', parseFloat(e.target.value))}
          className="w-full accent-indigo-500 cursor-pointer"
        />
        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>0</span>
          <span>10</span>
        </div>
      </section>
    </aside>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden md:block w-52 flex-shrink-0">{sidebar}</div>

      {/* Mobile drawer overlay */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="absolute inset-0 bg-black/40" onClick={onClose} />
          <div className="relative z-50 w-72 max-w-[85vw] bg-white dark:bg-slate-900 shadow-xl p-5 overflow-y-auto">
            {sidebar}
          </div>
        </div>
      )}
    </>
  )
}
