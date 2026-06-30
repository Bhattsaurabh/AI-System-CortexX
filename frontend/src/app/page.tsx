"use client";
import React, { useState, useRef, useEffect } from 'react';

type StreamEvent = {
  type: string;
  agent: string;
  message: string;
  meta: any;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("chat");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [projectDir, setProjectDir] = useState("");
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [theme, setTheme] = useState("glass");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const downloadChat = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(events, null, 2));
    const node = document.createElement('a');
    node.setAttribute("href", dataStr);
    node.setAttribute("download", "CortexX-chat-log.json");
    document.body.appendChild(node);
    node.click();
    node.remove();
  };

  const executeCopilot = async () => {
    if (!query.trim()) return;
    setLoading(true);
    
    // Append the user's query to the chat history
    setEvents((prev) => [
      ...prev, 
      { type: 'query', agent: 'User', message: query, meta: {} }
    ]);
    
    // Clear the input bar
    setQuery("");
    
    try {
      const backendUrl = `/api/v1/agent/stream`;
      const res = await fetch(backendUrl, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Bypass-Tunnel-Reminder": "true" 
        },
        body: JSON.stringify({ 
          query,
          mode,
          model,
          project_dir: projectDir
        })
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text.substring(0, 100)}`);
      }
      
      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("text/event-stream")) {
        const text = await res.text();
        throw new Error(`Expected stream but got ${contentType}: ${text.substring(0, 200)}`);
      }

      if (!res.body) throw new Error("No readable stream");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let aiResponseText = "";
      
      while (true) {
        const { value, done } = await reader.read();
        
        if (value) {
          const chunk = decoder.decode(value, { stream: !done });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '');
              try {
                const event: StreamEvent = JSON.parse(dataStr);
                
                if (event.agent === "AI Copilot" && event.type === "action") {
                  aiResponseText += event.message;
                  setEvents((prev) => {
                    const newEvents = [...prev];
                    const last = newEvents[newEvents.length - 1];
                    if (last && last.agent === "AI Copilot" && last.type === "action") {
                      last.message = aiResponseText;
                      return newEvents;
                    }
                    return [...newEvents, { ...event, message: aiResponseText }];
                  });
                } else {
                  setEvents((prev) => [...prev, event]);
                }
              } catch (e) {}
            }
          }
        }
        
        if (done) break;

      }
    } catch (err: any) {
      setEvents([{ type: 'error', agent: 'System', message: `Error: ${err.message || 'Unknown error'}`, meta: {} }]);
    }
    
    setLoading(false);
  };

  return (
    <main className={`min-h-screen p-8 font-sans relative overflow-hidden transition-colors duration-500 ${theme === 'glass' ? 'bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 text-white' : 'bg-gray-950 text-gray-100'}`}>
      {/* Decorative background blur blobs */}
      {theme === 'glass' && (
        <>
          <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-50 animate-pulse"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-50 animate-pulse" style={{ animationDelay: '2s' }}></div>
        </>
      )}

      <div className="max-w-4xl mx-auto relative z-10">
        
        {/* Top Action Bar */}
        <div className="flex justify-end gap-3 mb-2">
          <button onClick={() => setTheme(theme === 'glass' ? 'dark' : 'glass')} className="p-2.5 bg-white/10 hover:bg-white/20 rounded-full backdrop-blur-md transition-all border border-white/10 text-lg shadow-sm flex items-center justify-center w-12 h-12" title="Toggle Theme Mode">
            {theme === 'glass' ? '🌙' : '✨'}
          </button>
          <button onClick={downloadChat} disabled={events.length === 0} className="p-2.5 bg-white/10 hover:bg-blue-500/50 disabled:opacity-30 rounded-full backdrop-blur-md transition-all border border-white/10 text-lg shadow-sm flex items-center justify-center w-12 h-12" title="Export Chat Log">
            📥
          </button>
          <button onClick={() => setEvents([])} disabled={events.length === 0} className="p-2.5 bg-white/10 hover:bg-red-500/50 disabled:opacity-30 rounded-full backdrop-blur-md transition-all border border-white/10 text-lg shadow-sm flex items-center justify-center w-12 h-12" title="Clear Chat History">
            🗑️
          </button>
        </div>

        <header className="mb-10 text-center">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 mb-4 tracking-tight drop-shadow-sm">
            CortexX
          </h1>
          <p className="text-white/70 text-lg font-light tracking-wide">Ask me anything. I can write code, analyze architecture, tell stories, or plan your schedule.</p>
        </header>

        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-6 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] mb-8">
          
          {/* Mode Toggle */}
          <div className="flex justify-center mb-8">
            <div className="bg-black/20 backdrop-blur-md p-1.5 rounded-full inline-flex border border-white/10 shadow-inner">
              <button 
                onClick={() => setMode("chat")}
                className={`px-6 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 ease-in-out ${mode === 'chat' ? 'bg-white/20 text-white shadow-lg backdrop-blur-md' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
              >
                💬 General Chat
              </button>
              <button 
                onClick={() => setMode("builder")}
                className={`px-6 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 ease-in-out ${mode === 'builder' ? 'bg-white/20 text-white shadow-lg backdrop-blur-md' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
              >
                🏗️ Project Builder
              </button>
            </div>
          </div>

          {/* Builder Settings (Hidden in Chat Mode) */}
          {mode === "builder" && (
            <div className="flex flex-wrap gap-6 mb-6 pb-6 border-b border-white/10">
              <div className="flex-1 min-w-[250px]">
                <label className="block text-xs text-white/60 mb-2 font-medium tracking-wide">LLM Model</label>
                <select 
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-black/20 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/40 transition-all text-sm appearance-none cursor-pointer"
                >
                  <option className="bg-slate-800" value="gemini-2.5-flash">Gemini 2.5 Flash (Fast & Reliable)</option>
                  <option className="bg-slate-800" value="gemini-2.0-flash">Gemini 2.0 Flash (Next-Gen Speed)</option>
                  <option className="bg-slate-800" value="gemini-1.5-flash">Gemini 1.5 Flash (Legacy)</option>
                </select>
              </div>
              
              <div className="flex-[2] min-w-[300px]">
                <label className="block text-xs text-white/60 mb-2 font-medium tracking-wide">Target Project Directory</label>
                <input 
                  type="text" 
                  value={projectDir}
                  onChange={(e) => setProjectDir(e.target.value)}
                  placeholder="Absolute path to workspace folder..."
                  className="w-full bg-black/20 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/40 transition-all text-sm font-mono placeholder-white/30"
                />
              </div>
            </div>
          )}

          <div className="flex gap-4 relative items-center">
            <div className="relative flex-1 group">
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && executeCopilot()}
                placeholder="Type your message here..." 
                className="w-full bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl px-6 py-4 pr-12 text-white focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/40 transition-all text-base placeholder-white/40 shadow-inner" 
              />
              {query && (
                <button 
                  onClick={() => setQuery("")}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-white/50 hover:text-white bg-black/30 hover:bg-black/50 rounded-full w-8 h-8 flex items-center justify-center transition-all backdrop-blur-sm border border-white/5"
                  title="Clear text"
                >
                  ✕
                </button>
              )}
            </div>
            <button 
              onClick={executeCopilot}
              disabled={loading}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-md border border-white/20 disabled:opacity-50 text-white px-8 py-4 rounded-2xl font-semibold transition-all shadow-[0_4px_15px_rgba(0,0,0,0.1)] hover:shadow-[0_8px_25px_rgba(255,255,255,0.15)] flex-shrink-0"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Processing...
                </span>
              ) : "Generate"}
            </button>
          </div>
        </div>

        {events.length > 0 && (
          <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_8px_32px_0_rgba(31,38,135,0.2)] relative overflow-hidden min-h-[40vh]">
            <div className="space-y-6 max-h-[65vh] overflow-y-auto pr-4 pb-8 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
              {events.map((ev, idx) => (
                <div key={idx} className={`p-6 rounded-2xl border backdrop-blur-md flex gap-5 transition-all ${
                  ev.agent === 'User' ? 'border-white/10 bg-white/10 shadow-lg ml-8' : 
                  ev.agent === 'AI Copilot' ? 'border-white/5 bg-black/20 shadow-xl mr-8' : 
                  ev.type === 'thought' ? 'border-transparent bg-transparent opacity-70 ml-8' : 
                  ev.type === 'complete' ? 'border-green-400/20 bg-green-400/10 text-center mx-auto w-fit' :
                  'border-red-400/30 bg-red-400/10 text-red-200 mx-8'
                }`}>
                  {ev.type !== 'complete' && (
                    <div className="shrink-0 pt-1 text-2xl drop-shadow-md">
                      {ev.agent === 'User' ? '👤' : 
                       ev.agent === 'AI Copilot' ? '✨' : 
                       ev.type === 'thought' ? '⚙️' : '⚠️'}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    {ev.type !== 'complete' && (
                      <div className="flex items-center justify-between mb-3">
                        <span className={`font-semibold text-sm tracking-wide ${ev.agent === 'User' ? 'text-blue-200' : ev.agent === 'AI Copilot' ? 'text-purple-200' : 'text-white/60'}`}>
                          {ev.agent}
                        </span>
                        {ev.meta?.model && (
                          <span className="text-xs bg-black/30 border border-white/10 px-3 py-1 rounded-full text-white/70 font-mono shadow-inner">
                            {ev.meta.model}
                          </span>
                        )}
                      </div>
                    )}
                      {ev.agent === 'AI Copilot' ? (
                        <div className="text-white/90 font-light leading-relaxed">
                          {ev.message.split(/(```[\s\S]*?```)/g).map((part, pIdx) => {
                            if (part.startsWith('```') && part.endsWith('```')) {
                              const match = part.match(/```([a-zA-Z0-9-]*)\n([\s\S]*?)```/);
                              const language = match && match[1] ? match[1] : 'code';
                              const code = match ? match[2] : part.slice(3, -3);
                              
                              return (
                                <div key={pIdx} className="my-6 rounded-xl overflow-hidden border border-white/10 shadow-[0_8px_30px_rgb(0,0,0,0.3)] bg-black/40 backdrop-blur-2xl">
                                  <div className="flex items-center justify-between px-5 py-3 bg-black/40 border-b border-white/10">
                                    <span className="text-xs text-white/50 font-mono uppercase tracking-widest">{language}</span>
                                    <button 
                                      onClick={() => navigator.clipboard.writeText(code)}
                                      className="text-xs text-white/70 hover:text-white flex items-center gap-2 transition-all bg-white/5 hover:bg-white/10 border border-white/5 px-3 py-1.5 rounded-lg"
                                      title="Copy code"
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                      Copy
                                    </button>
                                  </div>
                                  <div className="p-5 overflow-x-auto">
                                    <pre className="text-sm font-mono text-blue-100/90 leading-relaxed">
                                      <code>{code}</code>
                                    </pre>
                                  </div>
                                </div>
                              );
                            }
                            return <span key={pIdx}>{part}</span>;
                          })}
                        </div>
                      ) : (
                        <div className={`text-base font-light leading-relaxed ${ev.agent === 'User' ? 'text-white' : ev.type === 'thought' ? 'text-white/60 text-sm' : 'text-white/90'}`}>
                          {ev.message}
                        </div>
                      )}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
            {/* Soft fade out at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#111322] to-transparent pointer-events-none rounded-b-3xl"></div>
          </div>
        )}
      </div>
    </main>
  );
}
