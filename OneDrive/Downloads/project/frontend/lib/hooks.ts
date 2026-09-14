"use client";
import { useCallback, useEffect, useState } from "react";

/** Small shared request hook for client pages that need loading/error state. */
export function useApi<T>(loader: () => Promise<T>, dependencies: unknown[] = []) {
  const [data, setData] = useState<T>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const reload = useCallback(() => {
    setLoading(true);
    setError(undefined);
    return loader().then(setData).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Request failed");
    }).finally(() => setLoading(false));
    // Callers intentionally provide a stable loader/dependency list.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);
  useEffect(() => { void reload(); }, [reload]);
  return { data, loading, error, reload };
}
