import { useEffect, useState } from 'react';

// Умный компонент, который показывает скелетон только если загрузка > 500мс с плавным переходом
export function SmartSkeleton({ isLoading, children }: { isLoading: boolean; children: React.ReactNode }) {
  const [showSkeleton, setShowSkeleton] = useState(false);

  useEffect(() => {
    let showTimer: NodeJS.Timeout;
    let hideTimer: NodeJS.Timeout;
    
    if (isLoading) {
      // Показываем скелетон только если загрузка дольше 500мс
      showTimer = setTimeout(() => {
        setShowSkeleton(true);
      }, 500);
    } else {
      // Плавное скрытие
      setShowSkeleton(false);
      hideTimer = setTimeout(() => {
        setShowSkeleton(false);
      }, 300);
    }

    return () => {
      clearTimeout(showTimer);
      clearTimeout(hideTimer);
    };
  }, [isLoading]);

  if (!showSkeleton) return null;

  return <>{children}</>;
}

export function SkeletonLoader({ count = 1, height = 'h-20' }: { count?: number; height?: string }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`${height} bg-gray-700 rounded-lg overflow-hidden`}
        />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="card space-y-4">
      <div className="h-8 bg-gray-700 rounded w-3/4" />
      <div className="space-y-3">
        <div className="h-4 bg-gray-700 rounded w-full" />
        <div className="h-4 bg-gray-700 rounded w-5/6" />
        <div className="h-4 bg-gray-700 rounded w-4/6" />
      </div>
      <div className="flex gap-3 pt-4">
        <div className="h-10 bg-gray-700 rounded flex-1" />
        <div className="h-10 bg-gray-700 rounded flex-1" />
      </div>
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="card p-0 overflow-hidden">
      <div className="p-6 border-b border-gray-700 h-12 bg-gray-700" />
      <div className="space-y-0 divide-y divide-gray-700">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="p-6 flex gap-4">
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-700 rounded w-3/4" />
              <div className="h-3 bg-gray-700 rounded w-1/2" />
            </div>
            <div className="h-10 w-24 bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonGrid({ columns = 4 }: { columns?: number }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${columns} gap-4`}>
      {Array.from({ length: columns }).map((_, i) => (
        <div key={i} className="card space-y-3">
          <div className="h-6 bg-gray-700 rounded w-2/3" />
          <div className="h-8 bg-gray-700 rounded w-1/2" />
        </div>
      ))}
    </div>
  );
}
