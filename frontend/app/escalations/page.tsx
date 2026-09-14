"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import type { Escalation } from "../../lib/types";
import { Empty, ErrorState } from "../../components/ui";

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.escalations().then(setEscalations).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <p className="text-sm font-semibold uppercase tracking-widest text-teal">Workspace</p>
      <h1 className="mt-3 text-4xl font-semibold">Escalations</h1>
      <p className="mt-3 text-ink/60">Review enquiries that need a human follow-up.</p>
      {error ? (
        <div className="mt-8"><ErrorState message={error} /></div>
      ) : escalations.length === 0 ? (
        <div className="mt-8"><Empty message="The queue is clear." /></div>
      ) : (
        <div className="mt-8 divide-y divide-ink/10 rounded-2xl bg-white px-6 shadow-soft">
          {escalations.map((escalation) => (
            <Link href={`/escalations/${escalation.id}`} key={escalation.id} className="block py-5 hover:text-teal">
              <div className="flex justify-between">
                <span className="font-medium">#{escalation.id} · {escalation.reason}</span>
                <span className="text-xs uppercase">{escalation.status}</span>
              </div>
              <p className="mt-1 line-clamp-1 text-sm text-ink/50">{escalation.message}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
