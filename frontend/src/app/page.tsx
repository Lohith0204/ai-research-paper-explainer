"use client";

import { useState } from "react";
import Image from "next/image";
import UploadView from "@/components/UploadView";
import ResultsView from "@/components/ResultsView";

export default function Home() {
  const [paperId, setPaperId] = useState<string | null>(null);

  return (
    <main className="flex-1 w-full mx-auto max-w-6xl p-4 md:p-8">
      <header className="mb-12 flex flex-col md:flex-row items-center md:items-center gap-4 text-center md:text-left">
        <Image 
          src="/logo.png" 
          alt="AI Research Paper Explainer Logo" 
          width={64} 
          height={64} 
          className="rounded-xl shadow-sm bg-white"
        />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Research Paper Explainer</h1>
          <p className="mt-2 flex-1 text-slate-500">Upload your PDF or DOCX to instantly understand it.</p>
        </div>
      </header>
      
      {!paperId ? (
        <UploadView onUploadComplete={(id) => setPaperId(id)} />
      ) : (
        <ResultsView paperId={paperId} onReset={() => setPaperId(null)} />
      )}
    </main>
  );
}
