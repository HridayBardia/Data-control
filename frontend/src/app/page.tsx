"use client";

import React, { useState } from "react";
import { 
  Search, 
  Shield, 
  Terminal, 
  Sliders, 
  Globe, 
  Mail, 
  Network,
  Link2,
  Layers,
  ArrowRight,
  Bot,
  Sparkles,
  Activity,
  GitFork,
  FileSearch,
  Lock
} from "lucide-react";

// Types
interface KnowledgeAsset {
  id: string;
  title: string;
  entityType: string;
  content: string;
  metadata: Record<string, string>;
  chunks: string[];
}

interface AuditEntry {
  id: string;
  action: string;
  timestamp: string;
  user: string;
  prevHash: string;
  currentHash: string;
  payload: Record<string, unknown>;
}

interface Citation {
  id: number;
  title: string;
  entity_type: string;
  score: number;
}

// Cryptographic hashing simulator
const computeHash = (data: string): string => {
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(8, '0') + "f3e970cb48db92";
};

const createAuditEntry = (id: string, action: string, prevHash: string, payload: Record<string, unknown>): AuditEntry => {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const currentHash = computeHash(id + action + prevHash + JSON.stringify(payload));
  return {
    id,
    action,
    timestamp,
    user: "admin@atlascorp.com",
    prevHash,
    currentHash,
    payload
  };
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"search" | "rag" | "graph" | "governance" | "connectors" | "policy" | "security" | "analytics">("search");
  const [activeModel, setActiveModel] = useState("OpenAI gpt-4o");

  // Knowledge Assets State
  const [assets] = useState<KnowledgeAsset[]>([
    {
      id: "1",
      title: "Project Atlas Architecture Overview",
      entityType: "DOCUMENT",
      content: "Project Atlas is an AI-native Enterprise Intelligence Platform. It connects via APIs to Slack, Microsoft 365, Jira, and Salesforce, building a semantic graph. Security is enforced using Zero Trust architecture and Row Level Security in PostgreSQL.",
      metadata: { author: "CTO Office", source: "Confluence", classification: "CONFIDENTIAL" },
      chunks: [
        "Project Atlas is an AI-native Enterprise Intelligence Platform.",
        "It connects via APIs to Slack, Microsoft 365, Jira, and Salesforce, building a semantic graph.",
        "Security is enforced using Zero Trust architecture and Row Level Security in PostgreSQL."
      ]
    },
    {
      id: "2",
      title: "Vendor Agreement - OpenAI Inc",
      entityType: "CONTRACT",
      content: "This agreement governs the API usage, data privacy terms, and zero-data retention policies. All enterprise data sent to models is isolated to private subnets. SLA requires 99.99% uptime.",
      metadata: { department: "Legal", status: "Executed", classification: "RESTRICTED" },
      chunks: [
        "This agreement governs the API usage, data privacy terms, and zero-data retention policies.",
        "All enterprise data sent to models is isolated to private subnets. SLA requires 99.99% uptime."
      ]
    },
    {
      id: "3",
      title: "Weekly Sync Notes - Engineering",
      entityType: "MEETING",
      content: "Discussed migrating vectors from pgvector to dedicated index if search count exceeds 10M records. Implemented cryptographic audit chains on database write operations to verify data integrity.",
      metadata: { project: "Atlas Engine", date: "2026-07-08", classification: "INTERNAL" },
      chunks: [
        "Discussed migrating vectors from pgvector to dedicated index if search count exceeds 10M records.",
        "Implemented cryptographic audit chains on database write operations to verify data integrity."
      ]
    }
  ]);

  // Search Query & Hybrid Settings
  const [searchQuery, setSearchQuery] = useState("");
  const [vectorWeight, setVectorWeight] = useState(0.5);
  const [searchResults, setSearchResults] = useState<{ asset: KnowledgeAsset; chunk: string; score: number }[]>([]);

  // RAG Chat State
  const [chatQuery, setChatQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<{ sender: "user" | "bot"; text: string; citations?: Citation[] }[]>([
    {
      sender: "bot",
      text: "Hello! I am your Atlas AI Assistant. Ask me anything about your enterprise knowledge, documents, or compliance policies.",
      citations: []
    }
  ]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Policy simulator state
  const [simDept, setSimDept] = useState("Finance");
  const [simResult, setSimResult] = useState<string | null>(null);

  // Connectors
  const [connectors] = useState([
    { id: "slack", name: "Slack Integration", icon: Mail, type: "Messaging", status: "Connected", items: "12,430 items", lastSynced: "5 mins ago" },
    { id: "gworkspace", name: "Google Workspace", icon: Globe, type: "Files/Mail", status: "Connected", items: "48,901 items", lastSynced: "12 mins ago" },
    { id: "jira", name: "Jira Cloud", icon: Layers, type: "Tasks/Tickets", status: "Connected", items: "4,320 items", lastSynced: "1 hour ago" },
    { id: "github", name: "GitHub Enterprise", icon: Terminal, type: "Codebase", status: "Disconnected", items: "0 items", lastSynced: "Never" }
  ]);

  // Audit Logs State
  const [auditLogs] = useState<AuditEntry[]>(() => {
    const e1 = createAuditEntry("1", "SYSTEM_BOOTSTRAP", "genesis_salt_project_atlas_2026", { engine: "Atlas Ingestion Engine", status: "HEALTHY" });
    const e2 = createAuditEntry("2", "CONNECTOR_INITIALIZED", e1.currentHash, { id: "slack", scope: "read_channels" });
    const e3 = createAuditEntry("3", "CONNECTOR_INITIALIZED", e2.currentHash, { id: "gworkspace", scope: "read_drive" });
    return [e1, e2, e3];
  });

  // Handle Search Trigger
  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const results: { asset: KnowledgeAsset; chunk: string; score: number }[] = [];
    const queryTerms = searchQuery.toLowerCase().split(" ");

    assets.forEach(asset => {
      asset.chunks.forEach(chunk => {
        let matches = 0;
        queryTerms.forEach(term => {
          if (chunk.toLowerCase().includes(term)) matches++;
        });

        if (matches > 0) {
          const rawScore = (matches / queryTerms.length) * 0.7 + (vectorWeight * 0.3);
          results.push({
            asset,
            chunk,
            score: Math.min(0.99, Math.max(0.45, rawScore))
          });
        }
      });
    });

    results.sort((a, b) => b.score - a.score);
    setSearchResults(results);
  };

  // Handle RAG Chat
  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim() || isStreaming) return;

    const userText = chatQuery;
    setChatQuery("");
    setChatHistory(prev => [...prev, { sender: "user", text: userText }]);
    setIsStreaming(true);

    setTimeout(() => {
      setChatHistory(prev => [
        ...prev,
        {
          sender: "bot",
          text: `Based on your enterprise Knowledge Graph, ${userText} aligns with the Zero Trust security architecture and row-level access controls documented in Project Atlas [1].`,
          citations: [
            { id: 1, title: "Project Atlas Architecture Overview", entity_type: "DOCUMENT", score: 0.94 }
          ]
        }
      ]);
      setIsStreaming(false);
    }, 800);
  };

  // Run Policy Simulator
  const handleSimulatePolicy = () => {
    if (simDept === "Finance") {
      setSimResult("PASSED: Access Granted under 'Finance Dept Only' policy rule.");
    } else {
      setSimResult(`DENIED: User department '${simDept}' violates 'Finance Dept Only' access rule.`);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Header Bar */}
      <header className="border-b border-zinc-800/80 bg-zinc-950/60 backdrop-blur-xl sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Network className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-lg bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                ATLAS
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                AI Data Control Platform
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 font-medium">Universal Data Governance Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-zinc-900/80 p-1 rounded-xl border border-zinc-800 overflow-x-auto">
          {[
            { id: "search", label: "Hybrid Search", icon: Search },
            { id: "rag", label: "AI Chat", icon: Bot },
            { id: "graph", label: "Knowledge Graph", icon: GitFork },
            { id: "governance", label: "Governance & PII", icon: FileSearch },
            { id: "connectors", label: "Connectors", icon: Link2 },
            { id: "policy", label: "Policy Engine", icon: Lock },
            { id: "security", label: "Audit Ledger", icon: Shield },
            { id: "analytics", label: "Telemetry", icon: Activity }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as "search" | "rag" | "graph" | "governance" | "connectors" | "policy" | "security" | "analytics")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* User Profile */}
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-medium text-zinc-200">Admin User</p>
            <p className="text-[10px] text-zinc-500">Atlas Corp • Super Admin</p>
          </div>
          <div className="h-8 w-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold text-indigo-400">
            AC
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        
        {/* HYBRID SEARCH TAB */}
        {activeTab === "search" && (
          <div className="space-y-6 animate-fadeIn">
            {/* Search Input Bar */}
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl">
              <form onSubmit={handleSearch} className="flex gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-3.5 h-5 w-5 text-zinc-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search enterprise knowledge base (e.g. RLS, Zero Trust, OpenAI SLA)..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-12 pr-4 py-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                  />
                </div>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-3 rounded-xl text-sm transition flex items-center gap-2 shadow-lg shadow-indigo-600/20"
                >
                  Search
                  <ArrowRight className="h-4 w-4" />
                </button>
              </form>

              {/* Hybrid Weighting Slider */}
              <div className="mt-4 flex items-center gap-4 text-xs font-medium text-zinc-400">
                <Sliders className="h-4 w-4 text-zinc-500" />
                <span>Hybrid Fusion Weights:</span>
                <span className="text-zinc-300">BM25 Keyword ({Math.round((1 - vectorWeight) * 100)}%)</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={vectorWeight}
                  onChange={e => setVectorWeight(parseFloat(e.target.value))}
                  className="w-32 accent-indigo-500 cursor-pointer"
                />
                <span className="text-zinc-300">pgvector Cosine ({Math.round(vectorWeight * 100)}%)</span>
              </div>
            </div>

            {/* Results Grid */}
            {searchResults.length > 0 ? (
              <div className="space-y-4">
                <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                  Top RRF Hybrid Results ({searchResults.length})
                </p>
                {searchResults.map((res, idx) => (
                  <div key={idx} className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-5 hover:border-zinc-700 transition">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                          {res.asset.entityType}
                        </span>
                        <h3 className="text-sm font-semibold text-zinc-100">{res.asset.title}</h3>
                      </div>
                      <span className="text-xs font-mono font-semibold text-emerald-400">
                        Score: {(res.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-xs text-zinc-300 leading-relaxed bg-zinc-950/50 p-3 rounded-lg border border-zinc-800/50 font-mono">
                      &quot;{res.chunk}&quot;
                    </p>
                  </div>
                ))}
              </div>
            ) : searchQuery ? (
              <div className="text-center py-12 text-zinc-500 text-sm">
                No indexed chunks matched your search criteria.
              </div>
            ) : null}
          </div>
        )}

        {/* AI RAG CHAT TAB */}
        {activeTab === "rag" && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl space-y-4 flex flex-col h-[650px]">
            <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <h2 className="text-sm font-bold text-white">Enterprise AI Orchestrator Studio</h2>
              </div>
              <select
                value={activeModel}
                onChange={e => setActiveModel(e.target.value)}
                className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="OpenAI gpt-4o">OpenAI gpt-4o</option>
                <option value="Anthropic Claude 3.5 Sonnet">Anthropic Claude 3.5 Sonnet</option>
                <option value="Google Gemini 1.5 Pro">Google Gemini 1.5 Pro</option>
                <option value="Ollama nomic-embed-text (Local)">Ollama Local</option>
              </select>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {chatHistory.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-xl rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-indigo-600 text-white rounded-br-none"
                        : "bg-zinc-950 border border-zinc-800 text-zinc-200 rounded-bl-none"
                    }`}
                  >
                    <p>{msg.text}</p>

                    {/* Citations list */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-zinc-800/80 space-y-1">
                        <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">Citations:</p>
                        {msg.citations.map((c, i) => (
                          <div key={i} className="flex items-center justify-between text-[10px] text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded">
                            <span>[{c.id}] {c.title}</span>
                            <span className="font-mono text-emerald-400">{Math.round(c.score * 100)}% Match</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Input Form */}
            <form onSubmit={handleChat} className="flex gap-2 pt-2 border-t border-zinc-800">
              <input
                type="text"
                value={chatQuery}
                onChange={e => setChatQuery(e.target.value)}
                placeholder={`Ask ${activeModel}...`}
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={isStreaming}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2.5 rounded-xl text-xs transition flex items-center gap-1 shadow-md shadow-indigo-600/20"
              >
                Send
              </button>
            </form>
          </div>
        )}

        {/* KNOWLEDGE GRAPH TAB */}
        {activeTab === "graph" && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <GitFork className="h-4 w-4 text-indigo-400" />
                Knowledge Graph Adjacency Explorer
              </h2>
              <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                Automatic Node & Link Resolution
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 space-y-3 font-mono text-xs">
                <p className="text-zinc-400 font-bold uppercase text-[10px]">Extracted Graph Entities (Nodes)</p>
                <div className="space-y-2">
                  <div className="p-2.5 bg-zinc-900 rounded border border-zinc-800 flex justify-between items-center">
                    <span className="text-indigo-400 font-bold">doc_1</span>
                    <span className="text-zinc-400 text-[10px]">Project Atlas Architecture Overview</span>
                    <span className="text-emerald-400 text-[10px]">DOCUMENT</span>
                  </div>
                  <div className="p-2.5 bg-zinc-900 rounded border border-zinc-800 flex justify-between items-center">
                    <span className="text-indigo-400 font-bold">usr_cto_office</span>
                    <span className="text-zinc-400 text-[10px]">CTO Office</span>
                    <span className="text-purple-400 text-[10px]">USER</span>
                  </div>
                  <div className="p-2.5 bg-zinc-900 rounded border border-zinc-800 flex justify-between items-center">
                    <span className="text-indigo-400 font-bold">tech_pgvector</span>
                    <span className="text-zinc-400 text-[10px]">pgvector</span>
                    <span className="text-cyan-400 text-[10px]">TECHNOLOGY</span>
                  </div>
                </div>
              </div>

              <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 space-y-3 font-mono text-xs">
                <p className="text-zinc-400 font-bold uppercase text-[10px]">Relationships (Edges)</p>
                <div className="space-y-2">
                  <div className="p-2.5 bg-zinc-900 rounded border border-zinc-800 flex items-center justify-between text-[11px]">
                    <span className="text-purple-400">usr_cto_office</span>
                    <span className="text-zinc-500 font-bold">--- AUTHORED ---&gt;</span>
                    <span className="text-indigo-400">doc_1</span>
                  </div>
                  <div className="p-2.5 bg-zinc-900 rounded border border-zinc-800 flex items-center justify-between text-[11px]">
                    <span className="text-indigo-400">doc_1</span>
                    <span className="text-zinc-500 font-bold">--- REFERENCES ---&gt;</span>
                    <span className="text-cyan-400">tech_pgvector</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* GOVERNANCE & PII TAB */}
        {activeTab === "governance" && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <FileSearch className="h-4 w-4 text-indigo-400" />
              Universal Data Governance & PII Scanner
            </h2>

            <div className="space-y-3">
              {assets.map(asset => (
                <div key={asset.id} className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 flex items-center justify-between font-mono text-xs">
                  <div>
                    <span className="font-bold text-white block mb-1">{asset.title}</span>
                    <span className="text-[10px] text-zinc-500">{asset.entityType} • {asset.content.substring(0, 70)}...</span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                      asset.metadata.classification === "RESTRICTED" ? "bg-red-500/10 text-red-400 border-red-500/20" :
                      asset.metadata.classification === "CONFIDENTIAL" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                      "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    }`}>
                      {asset.metadata.classification || "INTERNAL"}
                    </span>
                    <span className="text-[10px] text-zinc-400 bg-zinc-900 px-2 py-1 rounded border border-zinc-800">
                      Lineage Verified (18 steps)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* POLICY SIMULATOR TAB */}
        {activeTab === "policy" && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl space-y-4 max-w-xl mx-auto">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Lock className="h-4 w-4 text-indigo-400" />
              ABAC Policy Engine Simulator
            </h2>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-zinc-400 block mb-1">Simulated User Department</label>
                <select
                  value={simDept}
                  onChange={e => setSimDept(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Finance">Finance</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Marketing">Marketing</option>
                </select>
              </div>

              <button
                onClick={handleSimulatePolicy}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-xl text-xs transition shadow-md shadow-indigo-600/20"
              >
                Run Policy Evaluation
              </button>

              {simResult && (
                <div className={`p-4 rounded-xl text-xs font-mono border ${
                  simResult.startsWith("PASSED") ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"
                }`}>
                  {simResult}
                </div>
              )}
            </div>
          </div>
        )}

        {/* CONNECTORS TAB */}
        {activeTab === "connectors" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {connectors.map(c => {
              const Icon = c.icon;
              return (
                <div key={c.id} className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-5 flex flex-col justify-between hover:border-zinc-700 transition">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                        <Icon className="h-5 w-5 text-indigo-400" />
                      </div>
                      <div>
                        <h3 className="text-xs font-bold text-white">{c.name}</h3>
                        <p className="text-[10px] font-mono text-zinc-500">{c.type}</p>
                      </div>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                      c.status === "Connected" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-zinc-800 text-zinc-500 border-zinc-700"
                    }`}>
                      {c.status}
                    </span>
                  </div>

                  <div className="mt-4 pt-4 border-t border-zinc-800/60 flex items-center justify-between text-[11px] font-mono text-zinc-400">
                    <span>{c.items}</span>
                    <span>Synced {c.lastSynced}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* AUDIT LEDGER TAB */}
        {activeTab === "security" && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Shield className="h-4 w-4 text-indigo-400" />
                Tamper-Proof Cryptographic Audit Ledger
              </h2>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Chain Verified
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-zinc-800 text-zinc-400">
                    <th className="pb-2 font-semibold">ID</th>
                    <th className="pb-2 font-semibold">ACTION</th>
                    <th className="pb-2 font-semibold">TIMESTAMP</th>
                    <th className="pb-2 font-semibold">PREV HASH</th>
                    <th className="pb-2 font-semibold">CURRENT HASH</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/50 text-zinc-300">
                  {auditLogs.map(log => (
                    <tr key={log.id}>
                      <td className="py-2.5 font-bold text-zinc-400">#{log.id}</td>
                      <td className="py-2.5 text-indigo-400 font-semibold">{log.action}</td>
                      <td className="py-2.5 text-zinc-500">{log.timestamp}</td>
                      <td className="py-2.5 text-zinc-500 text-[10px]">{log.prevHash.substring(0, 16)}...</td>
                      <td className="py-2.5 text-emerald-400 text-[10px]">{log.currentHash.substring(0, 16)}...</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TELEMETRY TAB */}
        {activeTab === "analytics" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-5 space-y-2">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500">HTTP Requests (Total)</span>
              <p className="text-2xl font-bold font-mono text-white">189,420</p>
              <p className="text-[10px] text-emerald-400 font-mono">99.99% Success Rate</p>
            </div>
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-5 space-y-2">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500">Average RAG Latency</span>
              <p className="text-2xl font-bold font-mono text-white">128ms</p>
              <p className="text-[10px] text-emerald-400 font-mono">pgvector HNSW Optimized</p>
            </div>
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-5 space-y-2">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500">Celery Task Queue</span>
              <p className="text-2xl font-bold font-mono text-white">0 Pending</p>
              <p className="text-[10px] text-indigo-400 font-mono">Worker Capacity: 100%</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
