import { FileText } from "lucide-react";

export default function SummarySection({ data }: { data: any }) {
  if (!data) return (
    <Card>
      <p className="text-slate-500 italic">Summary not available.</p>
    </Card>
  );

  return (
    <Card title="Summary" icon={<FileText size={20} className="text-blue-500" />}>
      {data.tldr && (
        <div className="mb-4">
          <h3 className="font-semibold text-slate-800 text-sm uppercase tracking-wider mb-2">TL;DR</h3>
          <p className="text-slate-700 leading-relaxed bg-blue-50/50 p-4 rounded-lg font-medium">
            {data.tldr}
          </p>
        </div>
      )}
      
      {data.key_contributions && data.key_contributions.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-slate-800 text-sm uppercase tracking-wider mb-2">Key Contributions</h3>
          <ul className="list-disc pl-5 space-y-1 text-slate-600">
            {data.key_contributions.map((c: string, idx: number) => (
              <li key={idx}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {data.methodology && (
        <div className="mb-4">
          <h3 className="font-semibold text-slate-800 text-sm uppercase tracking-wider mb-2">Methodology</h3>
          <p className="text-slate-600 leading-relaxed text-sm">{data.methodology}</p>
        </div>
      )}

      {data.results && (
        <div>
          <h3 className="font-semibold text-slate-800 text-sm uppercase tracking-wider mb-2">Results</h3>
          <p className="text-slate-600 leading-relaxed text-sm">{data.results}</p>
        </div>
      )}
    </Card>
  );
}

export function Card({ title, icon, children }: { title?: string; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {title && (
        <div className="border-b border-slate-100 px-6 py-4 flex items-center gap-3 bg-slate-50/50">
          {icon}
          <h2 className="font-semibold text-lg text-slate-800">{title}</h2>
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}