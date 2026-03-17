import { useQuery } from '@tanstack/react-query'
import { FileText, CheckCircle, Tag, Mail } from 'lucide-react'
import { fetchStats } from '../api/client.js'

const TILES = [
  { key: 'total_papers',   label: 'Total Papers',  icon: FileText,     color: 'text-indigo-500' },
  { key: 'annotated_count', label: 'Annotated',    icon: CheckCircle,  color: 'text-emerald-500' },
  { key: '_subfields',     label: 'Subfields',     icon: Tag,          color: 'text-violet-500' },
  { key: 'total_digests',  label: 'Digests Sent',  icon: Mail,         color: 'text-sky-500' },
]

function Skeleton() {
  return (
    <div className="h-6 w-16 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
  )
}

export default function StatsBar() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
  })

  function getValue(key) {
    if (!stats) return null
    if (key === '_subfields') return Object.keys(stats.papers_by_subfield ?? {}).length
    return stats[key] ?? 0
  }

  return (
    <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 grid grid-cols-2 sm:grid-cols-4 gap-4">
        {TILES.map(({ key, label, icon: Icon, color }) => (
          <div key={key} className="flex items-center gap-3">
            <div className={`flex-shrink-0 p-2 rounded-lg bg-slate-100 dark:bg-slate-800 ${color}`}>
              <Icon size={16} />
            </div>
            <div>
              {isLoading ? (
                <Skeleton />
              ) : (
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-100 leading-tight">
                  {(getValue(key) ?? 0).toLocaleString()}
                </p>
              )}
              <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
