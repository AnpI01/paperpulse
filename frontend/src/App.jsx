import { useCallback, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Sun, Moon, Play, Filter, Zap } from 'lucide-react'
import clsx from 'clsx'
import { useTheme } from './hooks/useTheme.js'
import { runPipeline } from './api/client.js'
import StatsBar from './components/StatsBar.jsx'
import SearchBar from './components/SearchBar.jsx'
import FilterSidebar from './components/FilterSidebar.jsx'
import PaperGrid from './components/PaperGrid.jsx'
import PaperModal from './components/PaperModal.jsx'

const EMPTY_FILTERS = { subfield: null, dateFrom: '', dateTo: '', minScore: 0 }

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const queryClient = useQueryClient()

  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [search, setSearch] = useState('')
  const [selectedPaper, setSelectedPaper] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const pipeline = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })

  const handleSearch = useCallback(v => setSearch(v), [])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">

      {/* Header */}
      <header className="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Zap size={14} className="text-white" />
            </div>
            <span className="font-bold text-sm tracking-tight text-slate-900 dark:text-slate-100">
              PaperPulse
            </span>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Pipeline status */}
            {pipeline.isPending && (
              <span className="text-xs text-indigo-500 animate-pulse hidden sm:block">
                Running pipeline…
              </span>
            )}
            {pipeline.isSuccess && (
              <span className="text-xs text-emerald-500 hidden sm:block">
                Pipeline complete ✓
              </span>
            )}
            {pipeline.isError && (
              <span className="text-xs text-rose-500 hidden sm:block">
                Pipeline failed
              </span>
            )}

            {/* Run pipeline */}
            <button
              onClick={() => pipeline.mutate()}
              disabled={pipeline.isPending}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
                pipeline.isPending
                  ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white',
              )}
            >
              <Play size={11} />
              <span className="hidden sm:inline">Run Pipeline</span>
            </button>

            {/* Mobile filter toggle */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Open filters"
            >
              <Filter size={16} />
            </button>

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </div>
      </header>

      {/* Stats bar */}
      <StatsBar />

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Search */}
        <SearchBar onSearch={handleSearch} />

        {/* Two-column layout */}
        <div className="flex gap-6 mt-5">
          <FilterSidebar
            filters={filters}
            onFiltersChange={setFilters}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
          <PaperGrid
            filters={filters}
            search={search}
            onSelectPaper={setSelectedPaper}
          />
        </div>
      </main>

      {/* Paper detail modal */}
      {selectedPaper && (
        <PaperModal
          paper={selectedPaper}
          onClose={() => setSelectedPaper(null)}
        />
      )}
    </div>
  )
}
