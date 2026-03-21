"use client";

import { useState } from "react";
import { MessageSquare, Send, Loader2, User, Bot } from "lucide-react";
import { Card } from "./SummarySection";
import { api } from "@/lib/api";

export default function QASection({ paperId }: { paperId: string }) {
  const [messages, setMessages] = useState<{role: "user"|"ai", content: string, context?: any[]}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.askQuestion(paperId, userMsg);
      setMessages(prev => [...prev, { role: "ai", content: res.answer, context: res.context_used }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: "ai", content: "Sorry, I couldn't process that question." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Ask Questions" icon={<MessageSquare size={20} className="text-purple-500" />}>
      <div className="flex flex-col h-[400px]">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-3">
              <MessageSquare size={32} className="opacity-20" />
              <p>Ask anything about the paper...</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-blue-100 text-blue-600" : "bg-purple-100 text-purple-600"}`}>
                  {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`px-4 py-3 rounded-2xl max-w-[80%] ${msg.role === "user" ? "bg-blue-600 text-white rounded-tr-sm" : "bg-slate-100 text-slate-800 rounded-tl-sm"}`}>
                  <p className="text-sm shadow-sm">{msg.content}</p>
                  {msg.context && msg.context.length > 0 && (
                    <details className="mt-2 opacity-80 cursor-pointer">
                      <summary className="text-[10px] font-medium uppercase tracking-wider">Sources Used</summary>
                      <div className="mt-1 text-xs bg-black/5 p-2 rounded text-left">
                        {msg.context.map((c, idx) => (
                          <div key={idx} className="mb-1 truncate opacity-75">- "{c.text.substring(0,60)}..."</div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center">
                <Loader2 size={16} className="animate-spin" />
              </div>
              <div className="px-4 py-3 rounded-2xl bg-slate-100 max-w-[80%] rounded-tl-sm flex items-center">
                <div className="flex space-x-1">
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleAsk} className="relative mt-auto">
          <input
            type="text"
            className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </Card>
  );
}