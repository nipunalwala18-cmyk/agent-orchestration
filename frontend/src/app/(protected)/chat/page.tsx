"use client";

import { useState, useRef, useEffect } from "react";
import { useAuthStore } from "../../../store/auth";
import { Send, Bot, User, Trash2, UploadCloud } from "lucide-react";
import { api } from "../../../services/api";

interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  citations?: Array<{ source: string; chunk_index: number; text: string; score: number }>;
}

export default function ChatPage() {
  const { accessToken } = useAuthStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const savedHistory = localStorage.getItem("chat_history");
    if (savedHistory) {
      setMessages(JSON.parse(savedHistory));
    }
  }, []);

  const saveHistory = (history: Message[]) => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !accessToken) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_name", file.name);

    try {
      const response = await api.post("/v1/rag/upload", formData);

      const payload = response.data;
      const uploadMessage: Message = {
        id: crypto.randomUUID(),
        sender: "assistant",
        text: `Uploaded ${file.name}. The document is now available for RAG questions.`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      const nextMessages = [...messages, uploadMessage];
      setMessages(nextMessages);
      saveHistory(nextMessages);
    } catch (err: any) {
      console.error("Upload error:", err);
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        sender: "assistant",
        text: `Upload failed: ${err?.message || "Unknown error"}. Please try a PDF or text file.`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      const nextMessages = [...messages, errorMessage];
      setMessages(nextMessages);
      saveHistory(nextMessages);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessageText = input.trim();
    setInput("");

    const newMsg: Message = {
      id: crypto.randomUUID(),
      sender: "user",
      text: userMessageText,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    const updatedMessages = [...messages, newMsg];
    setMessages(updatedMessages);
    saveHistory(updatedMessages);

    setLoading(true);

    // Prepare Assistant response bubble
    const assistantMsgId = crypto.randomUUID();
    const botMsg: Message = {
      id: assistantMsgId,
      sender: "assistant",
      text: "",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, botMsg]);

    try {
      const ragResponse = await api.post(
        "/v1/rag/query",
        new URLSearchParams({ question: userMessageText, top_k: "3" }).toString(),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      const result = ragResponse.data.data ?? {};
      const answerText = result.answer || "No answer available.";
      const citations = result.citations || [];

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? { ...msg, text: answerText, citations }
            : msg
        )
      );

      setMessages((prev) => {
        saveHistory(prev);
        return prev;
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                text: "Error: Could not retrieve a connection to the streaming server.",
              }
            : msg
        )
      );
      setMessages((prev) => {
        saveHistory(prev);
        return prev;
      });
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem("chat_history");
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-[calc(100vh-8.5rem)] flex flex-col bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl overflow-hidden">
      {/* Thread Header */}
      <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-800/40">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-violet-600 dark:text-violet-400" />
          <div>
            <h3 className="font-bold text-zinc-900 dark:text-white text-sm">
              Sandbox Playground
            </h3>
            <p className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">
              SSE Stream Enabled
            </p>
          </div>
        </div>

        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            className="p-2 rounded-xl text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors duration-200"
            title="Clear Chat History"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Messages Pane */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto space-y-4">
            <div className="p-4 bg-violet-50 dark:bg-zinc-800 text-violet-600 dark:text-violet-400 rounded-3xl border border-violet-100 dark:border-zinc-700 shadow-md">
              <Bot className="h-10 w-10" />
            </div>
            <h4 className="font-bold text-zinc-900 dark:text-white text-lg">
              Sandbox Stream Console
            </h4>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
              Test out the platform&apos;s async streaming API. Submit any prompt,
              and watch the response parse word-by-word in real time.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3.5 max-w-[80%] ${
              msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
            }`}
          >
            <div
              className={`h-9 w-9 rounded-xl flex items-center justify-center shrink-0 border ${
                msg.sender === "user"
                  ? "bg-violet-600 text-white border-violet-700"
                  : "bg-zinc-50 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 border-zinc-200 dark:border-zinc-700"
              }`}
            >
              {msg.sender === "user" ? (
                <User className="h-5 w-5" />
              ) : (
                <Bot className="h-5 w-5" />
              )}
            </div>

            <div
              className={`p-4 rounded-3xl ${
                msg.sender === "user"
                  ? "bg-violet-50 dark:bg-violet-950/40 text-violet-900 dark:text-violet-100 rounded-tr-none border border-violet-100 dark:border-violet-800"
                  : "bg-zinc-50 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none border border-zinc-100 dark:border-zinc-700"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.text || (
                  <span className="flex gap-1.5 items-center py-1">
                    <span className="h-2 w-2 rounded-full bg-violet-600 animate-bounce"></span>
                    <span className="h-2 w-2 rounded-full bg-violet-600 animate-bounce delay-150"></span>
                    <span className="h-2 w-2 rounded-full bg-violet-600 animate-bounce delay-300"></span>
                  </span>
                )}
              </p>
              {msg.sender === "assistant" && msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 border-t border-zinc-200 dark:border-zinc-700 pt-2">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                    Sources
                  </p>
                  <ul className="mt-1 space-y-1 text-xs text-zinc-600 dark:text-zinc-300">
                    {msg.citations.map((citation, index) => (
                      <li key={`${citation.source}-${index}`}>
                        <span className="font-medium">{citation.source}</span> · chunk {citation.chunk_index + 1}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <span className="block text-[10px] text-zinc-400 mt-2 text-right">
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSend}
        className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-800/20"
      >
        <div className="flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleUpload}
            className="hidden"
            accept=".pdf,.txt"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="p-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors"
            title="Upload a PDF or text document"
          >
            {uploading ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" /> : <UploadCloud className="h-4.5 w-4.5" />}
          </button>
          <div className="relative flex-1">
            <input
              type="text"
              required
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder="Ask a question about your uploaded documents..."
              className="block w-full py-3.5 pl-4 pr-12 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-2xl text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:focus:ring-violet-400 transition-colors"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="absolute right-2 p-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white shadow-md shadow-violet-500/10 transition-colors"
            >
              <Send className="h-4.5 w-4.5" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
