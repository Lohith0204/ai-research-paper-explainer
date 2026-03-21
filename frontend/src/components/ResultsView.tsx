"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Loader2, ArrowLeft } from "lucide-react";
import SummarySection from "./SummarySection";
import InsightsSection from "./InsightsSection";
import QASection from "./QASection";
import GraphSection from "./GraphSection";

export default function ResultsView({ paperId, onReset }: { paperId: string; onReset: () => void }) {
  const [data, setData] = useState<any>({
    summary: null,
    insights: null,
    graph: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [summary, insights, graph] = await Promise.all([
          api.getSummary(paperId),
          api.getInsights(paperId).catch(() => null),
          api.getGraph(paperId).catch(() => null),
        ]);
        
        setData({ summary, insights, graph });
      } catch (err: any) {
        console.error(err);
        setError(err?.response?.data?.detail || "Failed to load paper details.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [paperId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20">
        <Loader2 size={48} className="animate-spin text-blue-600 mb-4" />
        <p className="text-lg font-medium">Extracting insights and parsing paper data...</p>
        <p className="text-slate-500 mt-2">This may take a few moments.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-red-500">
        <p>{error}</p>
        <button onClick={onReset} className="mt-4 px-4 py-2 bg-slate-200 text-slate-800 rounded-lg">Go back</button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
      <div className="lg:col-span-3 mb-2">
        <button onClick={onReset} className="flex items-center text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors">
          <ArrowLeft size={16} className="mr-2" /> Upload another paper
        </button>
      </div>

      <div className="lg:col-span-2 space-y-6">
        <SummarySection data={data.summary} />
        <QASection paperId={paperId} />
      </div>

      <div className="space-y-6">
        <InsightsSection data={data.insights} />
        <GraphSection data={data.graph} />
      </div>
    </div>
  );
}