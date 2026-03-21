import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_URL = `${API_BASE}/api/papers`;

export const api = {
  uploadPaper: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await axios.post(API_URL, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  getSummary: async (paperId: string) => {
    const { data } = await axios.get(`${API_URL}/${paperId}/summary`);
    return data;
  },

  getInsights: async (paperId: string) => {
    const { data } = await axios.get(`${API_URL}/${paperId}/insights`);
    return data;
  },

  getGraph: async (paperId: string) => {
    const { data } = await axios.get(`${API_URL}/${paperId}/graph`);
    return data;
  },

  askQuestion: async (paperId: string, question: string) => {
    const { data } = await axios.post(`${API_URL}/${paperId}/ask`, { question });
    return data;
  },
};