import { Lightbulb, Tag } from "lucide-react";
import { Card } from "./SummarySection";

export default function InsightsSection({ data }: { data: any }) {
  if (!data) return null;

  return (
    <Card title="Key Insights" icon={<Lightbulb size={20} className="text-amber-500" />}>
      <div className="space-y-6">
        <InsightCategory title="Models & Architecture" items={data.models} color="bg-rose-100 text-rose-700" />
        <InsightCategory title="Datasets" items={data.datasets} color="bg-indigo-100 text-indigo-700" />
        <InsightCategory title="Techniques" items={data.techniques} color="bg-emerald-100 text-emerald-700" />
        <InsightCategory title="Metrics" items={data.metrics} color="bg-sky-100 text-sky-700" />
      </div>
    </Card>
  );
}

function InsightCategory({ title, items, color }: { title: string, items: string[], color: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {items.map((item, idx) => (
          <span key={idx} className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${color}`}>
            <Tag size={10} className="mr-1 opacity-70" />
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}