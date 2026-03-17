import { useQuery } from '@tanstack/react-query'
import { FileText } from 'lucide-react'
import { fetchPapers } from '../api/client.js'
import PaperCard from './PaperCard.jsx'

function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 space-y-3 animate-pulse">
      <div className="flex justify-between">
        <div className="h-5 w-24 bg-slate-200 dark:bg-slate-700 rounded-full" />
        <div className="h-5 w-10 bg-slate-200 dark:bg-slate-700 rounded-full" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-full bg-slate-200 dark:bg-slate-700 rounded" />
        <div className="h-4 w-4/5 bg-slate-200 dark:bg-slate-700 rounded" />
      </div>
      <div className="h-3 w-2/3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="h-3 w-full bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="h-3 w-5/6 bg-slate-200 dark:bg-slate-700 rounded" />
    </div>
  )
}

function EmptyState() {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-20 text-center">
      <div className="p-4 rounded-full bg-slate-100 dark:bg-slate-800 mb-4">
        <FileText size={28} className="text-slate-400" />
      </div>
      <p className="text-slate-600 dark:text-slate-400 font-medium">No papers found</p>
      <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">
        Try adjusting your filters or run the pipeline to fetch new papers.
      </p>
    </div>
  )
}

export default function PaperGrid({ filters, search, onSelectPaper }) {
  const { data: papers = [], isLoading, isError } = useQuery({
    queryKey: ['papers', filters],
    queryFn: () => fetchPapers(filters),
  })

  const filtered = search
    ? papers.filter(p => p.title.toLowerCase().includes(search.toLowerCase()))
    : papers

  if (isError) {
    return (
      <div className="col-span-full text-center py-10 text-rose-500 text-sm">
        Failed to load papers. Is the backend running?
      </div>
    )
  }

  return (
    <div className="flex-1 min-w-0">
      {/* Result count */}
      <p className="text-xs text-slate-400 dark:text-slate-500 mb-3 h-4">
        {!isLoading && `${filtered.length} paper${filtered.length !== 1 ? 's' : ''}`}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)
          : filtered.length === 0
            ? <EmptyState />
            : filtered.map(paper => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  onClick={() => onSelectPaper(paper)}
                />
              ))}
      </div>
    </div>
  )
}
