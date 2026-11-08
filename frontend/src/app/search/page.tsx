import { Suspense } from 'react';
import { LoadingSkeleton } from '@/components/LoadingSkeleton';
import SearchPageClient from './SearchPageClient';

export default function SearchPage() {
  return (
    <Suspense fallback={<SearchPageShell />}>
      <SearchPageClient />
    </Suspense>
  );
}

function SearchPageShell() {
  return (
    <div className="min-h-[calc(100vh-64px)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <div className="h-4 w-40 rounded bg-slate-700 animate-pulse mb-2" />
          <div className="h-8 w-64 rounded bg-slate-700 animate-pulse" />
        </div>
        <LoadingSkeleton />
      </div>
    </div>
  );
}
