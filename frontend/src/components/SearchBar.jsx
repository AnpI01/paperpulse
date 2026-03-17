import { useEffect, useRef, useState } from 'react'
import { Search, X } from 'lucide-react'

/** Debounced search input. Calls onSearch after 300ms idle. */
export default function SearchBar({ onSearch }) {
  const [value, setValue] = useState('')
  const timer = useRef(null)

  useEffect(() => {
    clearTimeout(timer.current)
    timer.current = setTimeout(() => onSearch(value), 300)
    return () => clearTimeout(timer.current)
  }, [value, onSearch])

  return (
    <div className="relative w-full">
      <Search
        size={16}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
      />
      <input
        type="text"
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder="Search paper titles…"
        className="w-full pl-9 pr-9 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700
          bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100
          placeholder:text-slate-400 text-sm
          focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      />
      {value && (
        <button
          onClick={() => setValue('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
