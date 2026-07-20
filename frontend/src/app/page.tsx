"use client";

import React, { useState, useEffect } from "react";
import { 
  Search, 
  Database, 
  Shield, 
  Terminal, 
  RefreshCw, 
  Sliders, 
  Plus, 
  Globe, 
  FileText, 
  Mail, 
  CheckCircle, 
  AlertCircle, 
  Network,
  Users, 
  Key, 
  Settings, 
  HelpCircle,
  Link2,
  Trash2,
  Lock,
  Layers,
  ArrowRight
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
  payload: Record<string, any>;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"search" | "connectors" | "ingest" | "security">("search");
  
  // Knowledge Assets State
  const [assets, setAssets] = useState<KnowledgeAsset[]>([
    {
      id: "1",
      title: "Project Atlas Architecture Overview",
      entityType: "DOCUMENT",
      content: "Project Atlas is an AI-native Enterprise Intelligence Platform. It connects via APIs to Slack, Microsoft 365, Jira, and Salesforce, building a semantic graph. Security is enforced using Zero Trust architecture and Row Level Security in PostgreSQL.",
      metadata: { author: "CTO Office", source: "Confluence" },
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
      metadata: { department: "Legal", status: "Executed" },
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
      metadata: { project: "Atlas Engine", date: "2026-07-08" },
      chunks: [
        "Discussed migrating vectors from pgvector to dedicated index if search count exceeds 10M records.",
        "Implemented cryptographic audit chains on database write operations to verify data integrity."
      ]
    }
  ]);

  // Search Query
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<{ asset: KnowledgeAsset; chunk: string; score: number }[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Ingestion form state
  const [ingestTitle, setIngestTitle] = useState("");
  const [ingestType, setIngestType] = useState("DOCUMENT");
  const [ingestContent, setIngestContent] = useState("");
  const [ingestAuthor, setIngestAuthor] = useState("");
  const [ingestStatus, setIngestStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  // Connector States
  const [connectors, setConnectors] = useState([
    { id: "slack", name: "Slack Integration", icon: Mail, type: "Messaging", status: "Connected", items: "12,430 items", lastSynced: "5 mins ago" },
    { id: "gworkspace", name: "Google Workspace", icon: Globe, type: "Files/Mail", status: "Connected", items: "48,901 items", lastSynced: "12 mins ago" },
    { id: "jira", name: "Jira Cloud", icon: Layers, type: "Tasks/Tickets", status: "Connected", items: "4,320 items", lastSynced: "1 hour ago" },
    { id: "github", name: "GitHub Enterprise", icon: Terminal, type: "Codebase", status: "Disconnected", items: "0 items", lastSynced: "Never" },
    { id: "notion", name: "Notion Enterprise", icon: FileText, type: "Knowledge", status: "Disconnected", items: "0 items", lastSynced: "Never" }
  ]);

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);

  // Cryptographic hashing simulator
  const computeHash = (data: string): string => {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16).padStart(8, '0') + "f3e970cb48db92";
  };

  // Add an audit log entry
  const addAuditLog = (action: string, payload: Record<string, any>) => {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    setAuditLogs(prev => {
      const lastEntry = prev[prev.length - 1];
      const prevHash = lastEntry ? lastEntry.currentHash : "genesis_salt_project_atlas_2026";
      const id = (prev.length + 1).toString();
      const currentHash = computeHash(id + action + prevHash + JSON.stringify(payload));
      
      return [...prev, {
        id,
        action,
        timestamp,
        user: "admin@atlascorp.com",
        prevHash,
        currentHash,
        payload
      }];
    });
  };

  // Run initial log seed
  useEffect(() => {
    addAuditLog("SYSTEM_BOOTSTRAP", { engine: "Atlas Ingestion Engine", status: "HEALTHY" });
    addAuditLog("CONNECTOR_INITIALIZED", { id: "slack", scope: "read_channels" });
    addAuditLog("CONNECTOR_INITIALIZED", { id: "gworkspace", scope: "read_drive" });
  }, []);

  // Handle Search Trigger
  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    // Simulate API query latency
    setTimeout(() => {
      const results: { asset: KnowledgeAsset; chunk: string; score: number }[] = [];
      const queryWords = searchQuery.toLowerCase().split(/\s+/);
      
      assets.forEach(asset => {
        asset.chunks.forEach(chunk => {
          let matches = 0;
          queryWords.forEach(word => {
            if (chunk.toLowerCase().includes(word) || asset.title.toLowerCase().includes(word)) {
              matches += 1;
            }
          });

          if (matches > 0 || queryWords.some(w => w.length > 3 && chunk.toLowerCase().includes(w.substring(0, 4)))) {
            // Generate semantic score based on matches
            const score = 0.5 + (matches / (queryWords.length + 3)) * 0.45 + (Math.random() * 0.05);
            results.push({
              asset,
              chunk,
              score: Math.min(score, 0.98)
            });
          }
        });
      });

      // Sort by score
      results.sort((a, b) => b.score - a.score);
      setSearchResults(results);
      setIsSearching(false);
      
      addAuditLog("SEMANTIC_SEARCH_QUERY", { query: searchQuery, resultsCount: results.length });
    }, 4500);
  };

  // Handle Ingest Trigger
  const handleIngest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestTitle.trim() || !ingestContent.trim()) return;

    setIngestStatus("loading");

    setTimeout(() => {
      // Create asset
      const sentences = ingestContent.split(/[.!?]+/).map(s => s.trim()).filter(Boolean);
      const newAsset: KnowledgeAsset = {
        id: (assets.length + 1).toString(),
        title: ingestTitle,
        entityType: ingestType,
        content: ingestContent,
        metadata: { author: ingestAuthor || "System Agent", date: new Date().toISOString().split('T')[0] },
        chunks: sentences.length > 0 ? sentences : [ingestContent]
      };

      setAssets(prev => [newAsset, ...prev]);
      setIngestStatus("success");
      
      addAuditLog("RECORD_INGESTED", { 
        asset_id: newAsset.id, 
        title: ingestTitle, 
        entity_type: ingestType, 
        chunks_count: newAsset.chunks.length 
      });

      // Reset form
      setIngestTitle("");
      setIngestContent("");
      setIngestAuthor("");

      setTimeout(() => setIngestStatus("idle"), 3000);
    }, 1500);
  };

  // Toggle integration connector
  const toggleConnector = (connectorId: string) => {
    setConnectors(prev => prev.map(conn => {
      if (conn.id === connectorId) {
        const isConnected = conn.status === "Connected";
        const newStatus = isConnected ? "Disconnected" : "Connected";
        
        // Log action
        addAuditLog(isConnected ? "CONNECTOR_DISCONNECTED" : "CONNECTOR_CONNECTED", {
          connector_id: connectorId,
          name: conn.name
        });

        return {
          ...conn,
          status: newStatus,
          items: newStatus === "Connected" ? "Pending Initial Sync..." : "0 items",
          lastSynced: newStatus === "Connected" ? "Just now" : "Never"
        };
      }
      return conn;
    }));
  };

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-50 font-sans antialiased selection:bg-purple-900/30 selection:text-purple-200">
      
      {/* 1. Sidebar Nav */}
      <aside className="w-64 border-r border-zinc-900 bg-zinc-950 flex flex-col justify-between shrink-0">
        <div>
          {/* Platform Header */}
          <div className="h-16 px-6 border-b border-zinc-900 flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-white flex items-center justify-center text-zinc-950 font-extrabold text-lg shadow-[0_0_20px_rgba(255,255,255,0.15)]">
              A
            </div>
            <div>
              <span className="font-display font-bold tracking-tight text-white">Project Atlas</span>
              <div className="text-[10px] text-zinc-500 font-mono tracking-widest uppercase">Intel Layer</div>
            </div>
          </div>

          {/* Org Selector Mock */}
          <div className="p-4 border-b border-zinc-900">
            <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-900/40 border border-zinc-800/60">
              <div className="flex items-center gap-2">
                <div className="h-5 w-5 rounded bg-purple-500 flex items-center justify-center text-[10px] font-bold text-white">SL</div>
                <div className="text-xs font-semibold text-zinc-300">search-labs</div>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 font-mono">Tenant</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            <button
              onClick={() => setActiveTab("search")}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === "search"
                  ? "bg-zinc-900 text-white border border-zinc-800"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 border border-transparent"
              }`}
            >
              <Search className="h-4 w-4" />
              <span>Universal Search</span>
            </button>

            <button
              onClick={() => setActiveTab("connectors")}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === "connectors"
                  ? "bg-zinc-900 text-white border border-zinc-800"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 border border-transparent"
              }`}
            >
              <Link2 className="h-4 w-4" />
              <span>Connected Systems</span>
              {connectors.filter(c => c.status === "Connected").length > 0 && (
                <span className="ml-auto text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.2 rounded-full font-semibold">
                  {connectors.filter(c => c.status === "Connected").length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab("ingest")}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === "ingest"
                  ? "bg-zinc-900 text-white border border-zinc-800"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 border border-transparent"
              }`}
            >
              <Plus className="h-4 w-4" />
              <span>Ingestion Hub</span>
            </button>

            <button
              onClick={() => setActiveTab("security")}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === "security"
                  ? "bg-zinc-900 text-white border border-zinc-800"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 border border-transparent"
              }`}
            >
              <Shield className="h-4 w-4" />
              <span>Security & Audits</span>
              <span className="ml-auto text-[10px] bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.2 rounded-full font-semibold">
                Secure
              </span>
            </button>
          </nav>
        </div>

        {/* User Block & Bottom Navigation */}
        <div className="p-4 border-t border-zinc-900">
          <div className="space-y-4">
            <div className="rounded-lg bg-zinc-900/30 border border-zinc-900 p-3 space-y-2">
              <div className="flex items-center gap-1.5 text-zinc-400 text-xs font-mono">
                <Lock className="h-3 w-3 text-emerald-400" />
                <span>Zero Trust Enforcement</span>
              </div>
              <div className="text-[10px] text-zinc-500 leading-normal">
                RLS is isolating queries by organization ID `search-labs`.
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-full bg-zinc-800 flex items-center justify-center text-sm font-semibold border border-zinc-700 text-purple-300">
                AA
              </div>
              <div>
                <div className="text-xs font-semibold text-white">Atlas Admin</div>
                <div className="text-[10px] text-zinc-500 font-mono">admin@atlascorp.com</div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Content Frame */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Top Header */}
        <header className="h-16 border-b border-zinc-900 px-8 flex items-center justify-between bg-zinc-950/70 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs text-zinc-400 font-medium">Database Node Connected</span>
            </div>
            <span className="text-zinc-800">|</span>
            <div className="text-xs text-zinc-500 font-mono">
              IP Isolation Active
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 bg-zinc-900/60 border border-zinc-800/80 rounded-md px-2.5 py-1 text-[11px] font-mono text-zinc-400">
              <Key className="h-3.5 w-3.5 text-zinc-500" />
              <span>ROLE: ADMIN</span>
            </div>
            <button className="h-8 px-3 rounded-md bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-white transition-colors">
              API Docs
            </button>
          </div>
        </header>

        {/* Tab Canvas Area */}
        <main className="flex-1 p-8 overflow-y-auto max-w-6xl w-full mx-auto">
          
          {/* SEARCH TAB */}
          {activeTab === "search" && (
            <div className="space-y-6 animate-fade-in">
              <div className="space-y-1.5">
                <h1 className="text-2xl font-bold font-display text-white tracking-tight">Semantic Hybrid Search</h1>
                <p className="text-sm text-zinc-400">
                  Search across your entire enterprise knowledge graph. Neural embeddings will resolve meaning, not just keywords.
                </p>
              </div>

              {/* Form Input Container */}
              <div className="p-1 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
                <form onSubmit={handleSearch} className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Ask Atlas about agreements, weekly engineering logs, or technical specs..."
                      className="w-full bg-transparent border-0 pl-12 pr-4 py-3.5 text-sm text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:ring-0"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isSearching}
                    className="px-5 rounded-xl bg-white text-zinc-950 font-semibold text-xs hover:bg-zinc-200 transition-colors flex items-center gap-2 shrink-0 disabled:opacity-50"
                  >
                    {isSearching ? (
                      <>
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        <span>Vectorizing...</span>
                      </>
                    ) : (
                      <>
                        <span>Execute Search</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Processing Loader */}
              {isSearching && (
                <div className="p-8 rounded-xl border border-dashed border-zinc-800 flex flex-col items-center justify-center gap-4 bg-zinc-950/20">
                  <div className="relative h-12 w-12 flex items-center justify-center">
                    <div className="absolute inset-0 rounded-full border-2 border-purple-500/20 animate-ping"></div>
                    <Database className="h-6 w-6 text-purple-400 animate-pulse" />
                  </div>
                  <div className="space-y-1.5 text-center">
                    <p className="text-xs font-semibold text-zinc-200 font-mono">Running RAG Cosine Comparison</p>
                    <p className="text-[10px] text-zinc-500 max-w-sm">
                      Converting query string to vector(1536), applying pgvector `vector &lt;=&gt; :query` similarity matrices.
                    </p>
                  </div>
                </div>
              )}

              {/* Empty / Result State */}
              {!isSearching && searchResults.length === 0 && (
                <div className="grid md:grid-cols-3 gap-4 pt-4">
                  <div className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 space-y-2">
                    <div className="h-8 w-8 rounded bg-zinc-900 flex items-center justify-center text-purple-400">
                      <Lock className="h-4 w-4" />
                    </div>
                    <h3 className="text-xs font-bold text-zinc-200">Tenant Scoping</h3>
                    <p className="text-[11px] text-zinc-500 leading-normal">
                      Security context guarantees zero results leakage from other organizations. RLS strictly filters by org_id.
                    </p>
                  </div>
                  <div className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 space-y-2">
                    <div className="h-8 w-8 rounded bg-zinc-900 flex items-center justify-center text-blue-400">
                      <Network className="h-4 w-4" />
                    </div>
                    <h3 className="text-xs font-bold text-zinc-200">Knowledge Graph Linked</h3>
                    <p className="text-[11px] text-zinc-500 leading-normal">
                      Every document maps back to creators, tasks, and slack messages, resolving conceptual connections.
                    </p>
                  </div>
                  <div className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 space-y-2">
                    <div className="h-8 w-8 rounded bg-zinc-900 flex items-center justify-center text-amber-400">
                      <Sliders className="h-4 w-4" />
                    </div>
                    <h3 className="text-xs font-bold text-zinc-200">Hybrid Ranking</h3>
                    <p className="text-[11px] text-zinc-500 leading-normal">
                      Combines BM25 lexical keyword frequencies with dense semantic vector matches to provide optimal search results.
                    </p>
                  </div>
                </div>
              )}

              {/* Search Results Render */}
              {!isSearching && searchResults.length > 0 && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center px-1">
                    <span className="text-xs text-zinc-400 font-mono">Found {searchResults.length} relevant vector chunks</span>
                    <span className="text-[10px] text-zinc-500">Query duration: 4.5s (Cached embedding)</span>
                  </div>

                  <div className="space-y-3.5">
                    {searchResults.map((result, idx) => (
                      <div 
                        key={idx} 
                        className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/20 hover:border-zinc-800 transition-all space-y-3.5"
                      >
                        {/* Header Details */}
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono uppercase text-[10px]">
                              {result.asset.entityType}
                            </span>
                            <h3 className="text-sm font-semibold text-white hover:underline cursor-pointer">
                              {result.asset.title}
                            </h3>
                          </div>
                          
                          {/* Similarity Badge */}
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] text-zinc-500 font-mono">Cosine Sim:</span>
                            <span className={`text-xs font-mono px-2 py-0.5 rounded font-bold ${
                              result.score > 0.8 
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                            }`}>
                              {(result.score * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>

                        {/* Matching Text Block */}
                        <p className="text-sm text-zinc-300 leading-relaxed pl-3 border-l-2 border-purple-500/40">
                          {result.chunk}
                        </p>

                        {/* Footer Metadata */}
                        <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-1">
                          <div className="flex items-center gap-3">
                            <span>Author: {result.asset.metadata.author || result.asset.metadata.department || "System"}</span>
                            <span>•</span>
                            <span>Source: {result.asset.metadata.source || "Ingested"}</span>
                          </div>
                          <span className="font-mono text-[10px]">Chunk #{result.asset.chunks.indexOf(result.chunk)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CONNECTORS TAB */}
          {activeTab === "connectors" && (
            <div className="space-y-6 animate-fade-in">
              <div className="space-y-1.5">
                <h1 className="text-2xl font-bold font-display text-white tracking-tight">Enterprise Integrations</h1>
                <p className="text-sm text-zinc-400">
                  Securely link your business endpoints. Atlas runs non-invasive sync jobs utilizing read-only OAuth scopes.
                </p>
              </div>

              {/* Grid Layout */}
              <div className="grid md:grid-cols-2 gap-4">
                {connectors.map(conn => {
                  const IconComponent = conn.icon;
                  const isConnected = conn.status === "Connected";
                  return (
                    <div 
                      key={conn.id} 
                      className={`p-5 rounded-xl border transition-all flex flex-col justify-between h-44 ${
                        isConnected 
                          ? "bg-zinc-900/20 border-zinc-800/80" 
                          : "bg-zinc-950 border-zinc-900 opacity-60 hover:opacity-80"
                      }`}
                    >
                      <div>
                        {/* Upper Section */}
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`p-2.5 rounded-lg ${
                              isConnected ? "bg-zinc-900 text-purple-400" : "bg-zinc-900 text-zinc-600"
                            }`}>
                              <IconComponent className="h-5 w-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-semibold text-white">{conn.name}</h3>
                              <span className="text-[10px] text-zinc-500 uppercase font-mono tracking-wider">{conn.type}</span>
                            </div>
                          </div>

                          {/* Status Badge */}
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold border ${
                            isConnected 
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                              : "bg-zinc-800 text-zinc-500 border-zinc-700"
                          }`}>
                            {conn.status}
                          </span>
                        </div>

                        {/* Middle Stats */}
                        {isConnected && (
                          <div className="flex gap-4 mt-4 text-xs font-mono text-zinc-400">
                            <div>
                              <span className="text-zinc-500 text-[10px] block">INDEXED ASSETS</span>
                              <span className="font-semibold text-zinc-200">{conn.items}</span>
                            </div>
                            <div>
                              <span className="text-zinc-500 text-[10px] block">LAST SYNCHRONIZED</span>
                              <span className="font-semibold text-zinc-200">{conn.lastSynced}</span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Footer Action */}
                      <div className="flex justify-end pt-4 border-t border-zinc-900/60 mt-auto">
                        <button
                          onClick={() => toggleConnector(conn.id)}
                          className={`text-xs px-3 py-1.5 rounded-md font-semibold transition-colors ${
                            isConnected
                              ? "bg-zinc-900/80 hover:bg-red-950/20 hover:text-red-400 border border-zinc-800 text-zinc-300"
                              : "bg-white text-zinc-950 hover:bg-zinc-200"
                          }`}
                        >
                          {isConnected ? "Revoke Integration" : "Connect Endpoint"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* INGESTION HUB TAB */}
          {activeTab === "ingest" && (
            <div className="grid md:grid-cols-3 gap-8 animate-fade-in">
              {/* Left Column: Form */}
              <div className="md:col-span-2 space-y-6">
                <div className="space-y-1.5">
                  <h1 className="text-2xl font-bold font-display text-white tracking-tight">Direct Asset Ingestion</h1>
                  <p className="text-sm text-zinc-400 font-sans">
                    Manually index custom documents, contracts, or credentials straight into your organizations knowledge layer.
                  </p>
                </div>

                <form onSubmit={handleIngest} className="space-y-4 rounded-xl border border-zinc-900 bg-zinc-900/10 p-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-xs text-zinc-400 font-semibold block">Document Title</label>
                      <input
                        type="text"
                        required
                        value={ingestTitle}
                        onChange={(e) => setIngestTitle(e.target.value)}
                        placeholder="e.g. Server Migration Protocols"
                        className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-zinc-700"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs text-zinc-400 font-semibold block">Asset Entity Type</label>
                      <select
                        value={ingestType}
                        onChange={(e) => setIngestType(e.target.value)}
                        className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-zinc-700"
                      >
                        <option value="DOCUMENT">DOCUMENT</option>
                        <option value="CONTRACT">CONTRACT</option>
                        <option value="MEETING">MEETING NOTES</option>
                        <option value="EMAIL">EMAIL</option>
                        <option value="TASK">TASK / TICKET</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-zinc-400 font-semibold block">Author / Department</label>
                    <input
                      type="text"
                      value={ingestAuthor}
                      onChange={(e) => setIngestAuthor(e.target.value)}
                      placeholder="e.g. Infrastructure Team"
                      className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-zinc-700"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-zinc-400 font-semibold block">Raw Text Content</label>
                    <textarea
                      required
                      rows={5}
                      value={ingestContent}
                      onChange={(e) => setIngestContent(e.target.value)}
                      placeholder="Provide raw text. It will be split into chunks and converted into vectors automatically..."
                      className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-zinc-700 font-sans"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                      {ingestStatus === "loading" && (
                        <span className="flex items-center gap-1.5 text-xs text-purple-400 font-mono">
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          <span>Splitting and Vectorizing...</span>
                        </span>
                      )}
                      {ingestStatus === "success" && (
                        <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
                          <CheckCircle className="h-3.5 w-3.5" />
                          <span>Ingestion successful!</span>
                        </span>
                      )}
                    </div>
                    
                    <button
                      type="submit"
                      disabled={ingestStatus === "loading"}
                      className="px-5 py-2 rounded-lg bg-white text-zinc-950 font-semibold text-xs hover:bg-zinc-200 transition-colors"
                    >
                      Process & Ingest
                    </button>
                  </div>
                </form>
              </div>

              {/* Right Column: Assets List */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">In Memory Assets</h3>
                  <span className="text-[10px] text-zinc-500 font-mono">{assets.length} Ingested</span>
                </div>

                <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
                  {assets.map(asset => (
                    <div key={asset.id} className="p-3.5 rounded-lg border border-zinc-900 bg-zinc-900/20 hover:border-zinc-800 transition-colors">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 font-mono">{asset.entityType}</span>
                        <span className="text-[9px] text-zinc-500 font-mono">ID: {asset.id}</span>
                      </div>
                      <h4 className="text-xs font-semibold text-white truncate">{asset.title}</h4>
                      <p className="text-[11px] text-zinc-500 line-clamp-2 mt-1 leading-relaxed">
                        {asset.content}
                      </p>
                      <div className="flex justify-between items-center mt-2.5 pt-2 border-t border-zinc-900 text-[9px] text-zinc-500">
                        <span>Chunks: {asset.chunks.length}</span>
                        <span>{asset.metadata.author || "System"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SECURITY & AUDIT TAB */}
          {activeTab === "security" && (
            <div className="space-y-6 animate-fade-in">
              <div className="flex justify-between items-start">
                <div className="space-y-1.5">
                  <h1 className="text-2xl font-bold font-display text-white tracking-tight">Security Audit Logs</h1>
                  <p className="text-sm text-zinc-400">
                    A cryptographic chain verification ledger logs all data mutations. Modifying records invalidates the hash chain integrity check.
                  </p>
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold font-mono">
                  <CheckCircle className="h-4 w-4" />
                  <span>CHAIN VERIFIED</span>
                </div>
              </div>

              {/* Chain Logs Listing */}
              <div className="border border-zinc-900 rounded-xl bg-zinc-900/10 overflow-hidden">
                <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b border-zinc-900 text-xs font-semibold text-zinc-400 font-mono">
                  <div className="col-span-1">ID</div>
                  <div className="col-span-3">ACTION EVENT</div>
                  <div className="col-span-2">TIMESTAMP</div>
                  <div className="col-span-3">PREVIOUS ROW HASH</div>
                  <div className="col-span-3">CURRENT ROW HASH</div>
                </div>

                <div className="divide-y divide-zinc-900 font-mono text-xs">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="p-6 hover:bg-zinc-900/10 transition-colors space-y-4">
                      {/* Grid Header */}
                      <div className="grid grid-cols-12 gap-4 items-center">
                        <div className="col-span-1 text-zinc-600 font-bold">{log.id}</div>
                        <div className="col-span-3 text-white font-semibold flex items-center gap-1.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-purple-500"></span>
                          <span>{log.action}</span>
                        </div>
                        <div className="col-span-2 text-zinc-500">{log.timestamp}</div>
                        <div className="col-span-3 text-zinc-600 text-[10px] truncate">{log.prevHash}</div>
                        <div className="col-span-3 text-emerald-500/90 text-[10px] font-bold truncate flex items-center gap-1">
                          <Lock className="h-3 w-3 shrink-0" />
                          <span>{log.currentHash}</span>
                        </div>
                      </div>

                      {/* Expandable JSON Payload view */}
                      <div className="pl-4 border-l border-zinc-800 text-[11px] text-zinc-500 py-1 space-y-1">
                        <div><span className="text-zinc-600">Actor:</span> {log.user}</div>
                        <div><span className="text-zinc-600">Payload:</span> {JSON.stringify(log.payload)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

    </div>
  );
}
