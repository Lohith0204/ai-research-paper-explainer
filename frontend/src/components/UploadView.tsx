"use client";

import { useState } from "react";
import { UploadCloud, FileType, CheckCircle2, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function UploadView({ onUploadComplete }: { onUploadComplete: (id: string) => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorObj, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragover" || e.type === "dragenter") setIsDragging(true);
    else if (e.type === "dragleave" || e.type === "drop") setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (f: File) => {
    if (!f.name.endsWith(".pdf") && !f.name.endsWith(".docx")) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    setFile(f);
    setStatus("uploading");
    try {
      const res = await api.uploadPaper(f);
      // We no longer pre-calculate the complete analysis; rely on ResultsView
      // to parallelize fetching summary, insights, and graph sequentially.
      
      setStatus("success");
      setTimeout(() => onUploadComplete(res.paper_id), 1000);
    } catch (err: any) {
      console.error(err);
      setStatus("error");
      setError(err?.response?.data?.detail || "Analysis failed. Please try again.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white border border-slate-200 rounded-2xl shadow-sm max-w-2xl mx-auto mt-16">
      <div 
        className={`w-full relative py-16 px-12 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-colors cursor-pointer text-slate-500 hover:text-slate-700 hover:border-slate-400 ${
          isDragging ? "bg-blue-50 border-blue-400 text-blue-600" : "bg-slate-50 border-slate-300"
        }`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => {
          if (status !== "uploading") document.getElementById("file-upload")?.click();
        }}
      >
        <input
          id="file-upload"
          type="file"
          className="hidden"
          accept=".pdf,.docx"
          onChange={handleChange}
          disabled={status === "uploading"}
        />

        {status === "idle" || status === "error" ? (
          <>
            <UploadCloud size={48} className="mb-4 text-slate-400" />
            <p className="text-lg font-medium">Click or drag document to analyze</p>
            <p className="text-sm text-slate-400 mt-2">Supports PDF and DOCX</p>
            {errorObj && <p className="mt-4 text-red-500 font-medium text-sm text-center">{errorObj}</p>}
          </>
        ) : status === "uploading" ? (
          <>
            <Loader2 size={48} className="mb-4 animate-spin text-blue-600" />
            <p className="text-lg font-medium text-blue-600">Analyzing your paper...</p>
            <p className="text-sm mt-2 opacity-75">{file?.name}</p>
          </>
        ) : (
          <>
            <CheckCircle2 size={48} className="mb-4 text-green-500" />
            <p className="text-lg font-medium text-green-600">Successfully Uploaded!</p>
            <p className="text-sm mt-2 opacity-75">Redirecting to results...</p>
          </>
        )}
      </div>
    </div>
  );
}