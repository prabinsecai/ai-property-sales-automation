"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import type { Lead } from "../../lib/types";
import { Empty, ErrorState } from "../../components/ui";

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.leads().then(setLeads).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <p className="text-sm font-semibold uppercase tracking-widest text-teal">Workspace</p>
      <h1 className="mt-3 text-4xl font-semibold">Leads</h1>
      <p className="mt-3 text-ink/60">Review captured enquiries and qualification signals.</p>
      {error ? (
        <div className="mt-8"><ErrorState message={error} /></div>
      ) : leads.length === 0 ? (
        <div className="mt-8"><Empty message="No leads captured yet." /></div>
      ) : (
        <div className="mt-8 divide-y divide-ink/10 rounded-2xl bg-white px-6 shadow-soft">
          {leads.map((lead) => (
            <Link href={`/leads/${lead.id}`} key={lead.id} className="block py-5 hover:text-teal">
              <div className="flex justify-between">
                <span className="font-medium">{lead.name || lead.email || "Unnamed lead"}</span>
                <span className="text-sm">{lead.score}/100</span>
              </div>
              <p className="mt-1 text-sm text-ink/50">
                {lead.email || lead.phone || "No contact details"} · {lead.intent || "Property enquiry"}
                {lead.budget != null ? ` · Budget $${lead.budget.toLocaleString()}/wk` : ""}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
