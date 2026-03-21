"use client";

import { Share2 } from "lucide-react";
import { Card } from "./SummarySection";

export default function GraphSection({ data }: { data: any }) {
  if (!data || (!data.nodes && !data.edges)) return null;

  const nodes = data.nodes || [];
  const edges = data.edges || [];

  if (nodes.length === 0 && edges.length === 0) return null;

  return (
    <Card title="Knowledge Graph" icon={<Share2 size={20} className="text-orange-500" />}>
      <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        <p className="text-xs text-slate-500 mb-2">Entity Relationships</p>
        
        {edges.map((edge: any, i: number) => {
          const s = edge.source || edge.subject;
          const r = edge.relation || edge.predicate || "related to";
          const t = edge.target || edge.object;

          if (!s || !t) return null;

          return (
            <div key={i} className="flex flex-col bg-slate-50 border border-slate-100 p-3 rounded-lg text-sm">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-blue-700 bg-blue-100 px-2 py-0.5 rounded text-xs">{s}</span>
                <span className="text-slate-400 text-xs flex-1 shrink-0 px-2 text-center opacity-70">── {r} ──▶</span>
                <span className="font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded text-xs text-right">{t}</span>
              </div>
            </div>
          );
        })}

        {edges.length === 0 && nodes.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {nodes.map((node: any, i: number) => (
              <span key={i} className="px-3 py-1.5 bg-slate-100 rounded-md text-sm font-medium text-slate-700">
                {node.id || node}
              </span>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}