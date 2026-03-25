const isProd = process.env.NODE_ENV === "production";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || (isProd ? "" : "http://localhost:8000");
const API_URL = `${API_BASE}/api/papers`;

async function handleResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP error ${res.status}`);
  }
  return res.json();
}

export const api = {
  uploadPaper: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(API_URL, { method: "POST", body: formData });
    return handleResponse(res);
  },

  processFullPaper: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000);
    try {
      const res = await fetch(`${API_URL}/process`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
      return handleResponse(res);
    } finally {
      clearTimeout(timeout);
    }
  },

  getSummary: async (paperId: string) => {
    const res = await fetch(`${API_URL}/${paperId}/summary`);
    return handleResponse(res);
  },

  getInsights: async (paperId: string) => {
    const res = await fetch(`${API_URL}/${paperId}/insights`);
    return handleResponse(res);
  },

  getGraph: async (paperId: string) => {
    const res = await fetch(`${API_URL}/${paperId}/graph`);
    return handleResponse(res);
  },

  askQuestion: async (paperId: string, question: string) => {
    const res = await fetch(`${API_URL}/${paperId}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    return handleResponse(res);
  },
};