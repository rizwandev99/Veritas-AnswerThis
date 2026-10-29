"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Tooltip } from "@/components/ui/Tooltip";
import { ProgressStepper } from "@/components/ui/ProgressStepper";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ExternalLink,
  Share2,
  Download,
  Copy,
  Info,
  ChevronRight,
  Filter,
  Network,
  BookOpen,
} from "lucide-react";

interface Verification {
  claim_id: string;
  source_num: number;
  verdict: "supported" | "partial" | "unsupported" | "invalid_citation" | "unverifiable";
  confidence: number;
  evidence_quote: string;
  reasoning: string;
}

interface Claim {
  id: string;
  sentence: string;
  citations: number[];
  verdict: "supported" | "partial" | "unsupported" | "invalid_citation" | "unverifiable";
  confidence: number;
  verifications: Verification[];
}

interface Paper {
  source_num: number;
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  doi: string;
  url: string;
  abstract: string;
  citation_count: number;
  support_rate?: number;
}

export default function ReviewPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const reviewId = params?.id as string;
  const initialQuery = searchParams?.get("q") || "Transformer self-attention efficiency in long contexts";

  // State
  const [query, setQuery] = useState(initialQuery);
  const [status, setStatus] = useState<"loading" | "complete">("complete");
  const [currentStep, setCurrentStep] = useState(4);
  const [activeTab, setActiveTab] = useState<"review" | "graph" | "sources">("review");
  const [filterMode, setFilterMode] = useState<"all" | "flagged">("all");
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [selectedSource, setSelectedSource] = useState<number | null>(null);
  const [hoveredNode, setHoveredNode] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);

  // Mock papers grounded in PRD eval fixtures
  const papers: Paper[] = [
    {
      source_num: 1,
      id: "W2741809807",
      title: "Attention Is All You Need",
      authors: ["A. Vaswani", "N. Shazeer", "N. Parmar", "J. Uszkoreit"],
      year: 2017,
      venue: "NeurIPS",
      doi: "10.48550/arXiv.1706.03762",
      url: "https://doi.org/10.48550/arXiv.1706.03762",
      citation_count: 125400,
      support_rate: 1.0,
      abstract:
        "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
    },
    {
      source_num: 2,
      id: "W3091393630",
      title: "Longformer: The Long-Document Transformer",
      authors: ["I. Beltagy", "M. Peters", "A. Cohan"],
      year: 2020,
      venue: "arXiv",
      doi: "10.48550/arXiv.2004.05150",
      url: "https://doi.org/10.48550/arXiv.2004.05150",
      citation_count: 3200,
      support_rate: 1.0,
      abstract:
        "Transformer-based models are unable to process long sequences due to their self-attention operation, which scales quadratically with sequence length. To address this limitation, we introduce the Longformer with an attention mechanism that scales linearly with sequence length, making it easy to process documents of thousands of tokens or longer.",
    },
    {
      source_num: 3,
      id: "W2989938566",
      title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
      authors: ["T. Dao", "D. Fu", "S. Ermon", "A. Rudra", "C. Ré"],
      year: 2022,
      venue: "NeurIPS",
      doi: "10.48550/arXiv.2205.14135",
      url: "https://doi.org/10.48550/arXiv.2205.14135",
      citation_count: 4800,
      support_rate: 0.67,
      abstract:
        "Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are quadratic in sequence length. Approximate attention methods have attempted to address this, but often trade off model quality. We propose FlashAttention, an IO-aware exact attention algorithm that uses tiling to reduce memory reads/writes between GPU HBM and SRAM.",
    },
  ];

  const claims: Claim[] = [
    {
      id: "c-1",
      sentence:
        "Standard multi-head self-attention mechanisms exhibit a quadratic time and memory complexity O(N^2) relative to sequence length, creating prohibitive hardware constraints when processing long inputs.",
      citations: [1, 2],
      verdict: "supported",
      confidence: 0.96,
      verifications: [
        {
          claim_id: "c-1",
          source_num: 2,
          verdict: "supported",
          confidence: 0.98,
          evidence_quote: "which scales quadratically with sequence length",
          reasoning: "The cited text explicitly states that self-attention scales quadratically with sequence length.",
        },
      ],
    },
    {
      id: "c-2",
      sentence:
        "To mitigate quadratic scaling, sparse attention patterns such as those employed in Longformer reduce complexity to linear O(N) while maintaining task performance across multi-thousand token contexts.",
      citations: [2],
      verdict: "supported",
      confidence: 0.94,
      verifications: [
        {
          claim_id: "c-2",
          source_num: 2,
          verdict: "supported",
          confidence: 0.94,
          evidence_quote: "an attention mechanism that scales linearly with sequence length",
          reasoning: "Source 2 confirms the linear scaling attention mechanism designed for thousands of tokens.",
        },
      ],
    },
    {
      id: "c-3",
      sentence:
        "Hardware-aware exact attention architectures like FlashAttention completely eliminate GPU memory reads and achieve zero latency overhead regardless of sequence size.",
      citations: [3],
      verdict: "unsupported",
      confidence: 0.89,
      verifications: [
        {
          claim_id: "c-3",
          source_num: 3,
          verdict: "unsupported",
          confidence: 0.89,
          evidence_quote: "uses tiling to reduce memory reads/writes between GPU HBM and SRAM",
          reasoning:
            "Source 3 states that FlashAttention reduces memory reads/writes via tiling, contradicting the claim that it completely eliminates reads or achieves zero latency.",
        },
      ],
    },
    {
      id: "c-4",
      sentence:
        "IO-aware tiling allows exact attention computation by executing softmax operations on GPU SRAM without materializing large intermediate attention matrices in HBM.",
      citations: [3],
      verdict: "supported",
      confidence: 0.92,
      verifications: [
        {
          claim_id: "c-4",
          source_num: 3,
          verdict: "supported",
          confidence: 0.92,
          evidence_quote: "uses tiling to reduce memory reads/writes between GPU HBM and SRAM",
          reasoning: "Confirmed by FlashAttention abstract explaining SRAM tiling and reduced IO.",
        },
      ],
    },
  ];

  // Calculate Trust Score: (Supported + 0.5 * Partial) / Total Verifiable * 100
  const supportedCount = claims.filter((c) => c.verdict === "supported").length;
  const partialCount = claims.filter((c) => c.verdict === "partial").length;
  const trustScore = Math.round(((supportedCount + 0.5 * partialCount) / claims.length) * 100);

  const displayedClaims = claims.filter((c) => {
    if (filterMode === "flagged" && c.verdict === "supported") return false;
    if (selectedSource !== null && !c.citations.includes(selectedSource)) return false;
    return true;
  });

  const copyBibtex = () => {
    const bibtex = papers
      .map(
        (p) =>
          `@article{veritas_${p.id},\n  title = {${p.title}},\n  author = {${p.authors.join(" and ")}},\n  year = {${p.year}},\n  doi = {${p.doi}}\n}`
      )
      .join("\n\n");
    navigator.clipboard.writeText(bibtex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const copyMarkdown = () => {
    const md = `# ${query}\n\n${claims.map((c) => `${c.sentence} [${c.citations.join("][")}] (${c.verdict})`).join("\n\n")}\n\n## References\n${papers.map((p) => `[${p.source_num}] ${p.authors.join(", ")} (${p.year}). ${p.title}. DOI: ${p.doi}`).join("\n")}`;
    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background text-text-primary flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="font-bold tracking-tight text-base flex items-center gap-1.5 hover:opacity-80">
              <ShieldCheck className="w-5 h-5 text-accent" /> Veritas
            </Link>
            <span className="text-text-tertiary">/</span>
            <span className="text-xs font-mono text-text-secondary truncate max-w-[200px] sm:max-w-xs">
              {reviewId}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Button size="sm" variant="outline" onClick={copyMarkdown}>
              <Copy className="w-3.5 h-3.5 mr-1" /> {copied ? "Copied" : "Copy MD"}
            </Button>
            <Button size="sm" variant="outline" onClick={copyBibtex}>
              <Download className="w-3.5 h-3.5 mr-1" /> BibTeX
            </Button>
            <div className="h-4 w-px bg-border" />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Review Layout: Two Columns */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Title, Trust Score, Stepper, Review Text (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Query Title */}
          <div>
            <span className="text-xs font-semibold text-accent uppercase tracking-wider">Literature Review</span>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mt-1">
              {query}
            </h1>
          </div>

          {/* Trust Score Header Banner */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-lg bg-surface border border-border shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-accent-muted flex items-center justify-center font-bold text-accent text-lg">
                {trustScore}%
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-semibold text-text-primary">Citation Trust Score</span>
                  <Tooltip content="Verification is performed against abstracts (available text), not full papers. Formula: (Supported + 0.5 * Partial) / Total.">
                    <Info className="w-3.5 h-3.5 text-text-tertiary cursor-pointer hover:text-text-primary" />
                  </Tooltip>
                </div>
                <div className="text-xs text-text-secondary flex items-center gap-2 mt-0.5">
                  <span className="text-success flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> {supportedCount} Supported
                  </span>
                  <span>•</span>
                  <span className="text-danger flex items-center gap-1">
                    <XCircle className="w-3 h-3" /> {claims.length - supportedCount} Flagged
                  </span>
                </div>
              </div>
            </div>

            {/* Filter Toggle */}
            <div className="flex items-center gap-1 p-1 rounded-md bg-surface-elevated border border-border text-xs">
              <button
                type="button"
                onClick={() => setFilterMode("all")}
                className={`px-2.5 py-1 rounded-sm font-medium transition-colors ${
                  filterMode === "all" ? "bg-surface text-text-primary shadow-xs" : "text-text-secondary hover:text-text-primary"
                }`}
              >
                All Claims ({claims.length})
              </button>
              <button
                type="button"
                onClick={() => setFilterMode("flagged")}
                className={`px-2.5 py-1 rounded-sm font-medium transition-colors flex items-center gap-1 ${
                  filterMode === "flagged" ? "bg-surface text-danger shadow-xs" : "text-text-secondary hover:text-text-primary"
                }`}
              >
                <Filter className="w-3 h-3" /> Flagged ({claims.length - supportedCount})
              </button>
            </div>
          </div>

          {/* Stepper */}
          <ProgressStepper
            steps={[
              { id: "1", label: "Discovery" },
              { id: "2", label: "Ranking" },
              { id: "3", label: "Generation" },
              { id: "4", label: "Verification" },
            ]}
            currentStepIndex={currentStep}
          />

          {/* Review Text Body */}
          <Card className="p-6 space-y-6">
            <div className="border-b border-border pb-3 flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                Verified Synthesis
              </span>
              <span className="text-xs text-text-secondary">{displayedClaims.length} Claims Shown</span>
            </div>

            {selectedSource !== null && (
              <div className="flex items-center justify-between px-3 py-2 rounded-md bg-accent/10 border border-accent/30 text-xs">
                <span className="text-accent font-medium flex items-center gap-1.5">
                  <span className="font-mono font-bold">[{selectedSource}]</span> Filter active: {papers.find(p => p.source_num === selectedSource)?.title}
                </span>
                <button
                  onClick={() => setSelectedSource(null)}
                  className="text-text-tertiary hover:text-text-primary text-[11px] underline ml-2"
                >
                  Clear filter
                </button>
              </div>
            )}

            <div className="space-y-4 text-sm leading-relaxed text-text-primary">
              {displayedClaims.map((claim) => {
                const isSelected = selectedClaim?.id === claim.id;
                return (
                  <p
                    key={claim.id}
                    onClick={() => setSelectedClaim(claim)}
                    className={`p-3 rounded-md transition-all cursor-pointer border ${
                      isSelected
                        ? "bg-surface-elevated border-accent ring-1 ring-accent"
                        : "hover:bg-surface-elevated/60 border-transparent"
                    }`}
                  >
                    <span>{claim.sentence} </span>

                    {/* Inline Citation Chips & Verification Badges */}
                    <span className="inline-flex items-center gap-1.5 ml-1 select-none">
                      {claim.citations.map((cite) => (
                        <span
                          key={cite}
                          className="font-mono text-xs px-1.5 py-0.5 rounded bg-surface-elevated border border-border text-accent font-semibold"
                        >
                          [{cite}]
                        </span>
                      ))}

                      {claim.verdict === "supported" && (
                        <Badge variant="supported" interactive>
                          <CheckCircle2 className="w-3 h-3 text-success" /> Supported
                        </Badge>
                      )}
                      {claim.verdict === "partial" && (
                        <Badge variant="partial" interactive>
                          <AlertTriangle className="w-3 h-3 text-warning" /> Partial
                        </Badge>
                      )}
                      {claim.verdict === "unsupported" && (
                        <Badge variant="unsupported" interactive>
                          <XCircle className="w-3 h-3 text-danger" /> Unsupported
                        </Badge>
                      )}
                    </span>
                  </p>
                );
              })}
            </div>
          </Card>

          {/* Bottom References List */}
          <section className="space-y-3 pt-4">
            <h3 className="text-sm font-semibold tracking-tight text-text-primary">
              Cited References ({papers.length})
            </h3>
            <div className="space-y-2">
              {papers.map((p) => (
                <div
                  key={p.source_num}
                  className="p-3 rounded-lg bg-surface border border-border text-xs space-y-1 hover:border-accent/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-semibold text-accent">[{p.source_num}]</span>
                    <span className="text-text-tertiary font-mono">{p.year} • {p.venue}</span>
                  </div>
                  <div className="font-medium text-text-primary">{p.title}</div>
                  <div className="text-text-secondary">{p.authors.join(", ")}</div>
                  <div className="pt-1 flex items-center justify-between text-text-tertiary">
                    <span>{p.citation_count.toLocaleString()} citations</span>
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-accent hover:underline flex items-center gap-1"
                    >
                      DOI <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column: Context-Sensitive Evidence Panel or Citation Graph (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Top Panel Mode Switcher */}
          <div className="flex items-center gap-1 p-1 rounded-lg bg-surface border border-border">
            <button
              type="button"
              onClick={() => setActiveTab("review")}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                activeTab === "review"
                  ? "bg-surface-elevated text-text-primary shadow-xs border border-border"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" /> Evidence
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("graph")}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                activeTab === "graph"
                  ? "bg-surface-elevated text-text-primary shadow-xs border border-border"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <Network className="w-3.5 h-3.5" /> Graph
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("sources")}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                activeTab === "sources"
                  ? "bg-surface-elevated text-text-primary shadow-xs border border-border"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" /> Sources
            </button>
          </div>

          {/* Active Panel View */}
          {activeTab === "review" && (
            <Card elevated className="p-5 space-y-4 sticky top-20">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                  Claim Verification Audit
                </span>
                {selectedClaim && (
                  <Badge
                    variant={
                      selectedClaim.verdict === "supported"
                        ? "supported"
                        : selectedClaim.verdict === "partial"
                        ? "partial"
                        : "unsupported"
                    }
                  >
                    {selectedClaim.verdict.toUpperCase()} ({(selectedClaim.confidence * 100).toFixed(0)}%)
                  </Badge>
                )}
              </div>

              {selectedClaim ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-xs font-medium text-text-secondary">Selected Claim:</span>
                    <p className="text-xs text-text-primary bg-surface p-2.5 rounded border border-border mt-1 italic leading-relaxed">
                      "{selectedClaim.sentence}"
                    </p>
                  </div>

                  {selectedClaim.verifications.map((v, idx) => {
                    const paper = papers.find((p) => p.source_num === v.source_num);
                    return (
                      <div key={idx} className="space-y-2 pt-2 border-t border-border">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-accent">Source [{v.source_num}]: {paper?.title}</span>
                          <span className="font-mono text-text-tertiary">Conf: {(v.confidence * 100).toFixed(0)}%</span>
                        </div>

                        <div>
                          <span className="text-[11px] font-semibold text-text-tertiary uppercase tracking-wider">
                            Verbatim Grounding Quote:
                          </span>
                          <blockquote className="mt-1 p-2 rounded bg-surface border-l-2 border-accent text-xs font-mono text-text-primary leading-relaxed">
                            "{v.evidence_quote}"
                          </blockquote>
                        </div>

                        <div>
                          <span className="text-[11px] font-semibold text-text-tertiary uppercase tracking-wider">
                            Entailment Reasoning:
                          </span>
                          <p className="mt-0.5 text-xs text-text-secondary leading-relaxed">
                            {v.reasoning}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-text-tertiary space-y-2">
                  <HelpCircle className="w-6 h-6 mx-auto text-text-tertiary/60" />
                  <p>Click any cited sentence or badge in the review to inspect its grounding evidence and entailment check.</p>
                </div>
              )}
            </Card>
          )}

          {activeTab === "graph" && (
            <Card elevated className="p-5 space-y-4 sticky top-20">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                    Citation Network Graph
                  </span>
                  <p className="text-[11px] text-text-tertiary">Click any node to filter claims</p>
                </div>
                <div className="flex items-center gap-2">
                  {selectedSource !== null && (
                    <button
                      onClick={() => setSelectedSource(null)}
                      className="text-[11px] text-accent hover:underline font-mono"
                    >
                      Reset filter
                    </button>
                  )}
                  <span className="text-xs font-mono text-text-secondary bg-surface px-2 py-0.5 rounded border border-border">
                    3 Nodes • 2 Edges
                  </span>
                </div>
              </div>

              {/* Interactive SVG Network */}
              <div className="relative rounded-lg bg-surface border border-border overflow-hidden">
                <svg
                  viewBox="0 0 460 260"
                  className="w-full h-64 select-none"
                >
                  <defs>
                    <marker
                      id="arrow"
                      viewBox="0 0 10 10"
                      refX="26"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1 L 9 5 L 0 9 z" fill="#64748b" opacity="0.7" />
                    </marker>
                    <marker
                      id="arrow-active"
                      viewBox="0 0 10 10"
                      refX="26"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1 L 9 5 L 0 9 z" fill="#6366f1" />
                    </marker>
                  </defs>

                  {/* Edge: Longformer [2] -> Attention Is All You Need [1] */}
                  <path
                    d="M 135 75 Q 230 75 305 118"
                    fill="none"
                    stroke={selectedSource === 2 || selectedSource === 1 ? "#6366f1" : "#475569"}
                    strokeWidth={selectedSource === 2 || selectedSource === 1 ? 2.5 : 1.5}
                    strokeDasharray={selectedSource === 2 ? "4 2" : "none"}
                    markerEnd={selectedSource === 2 || selectedSource === 1 ? "url(#arrow-active)" : "url(#arrow)"}
                    className="transition-colors duration-200"
                  />

                  {/* Edge: FlashAttention [3] -> Attention Is All You Need [1] */}
                  <path
                    d="M 135 185 Q 230 185 305 142"
                    fill="none"
                    stroke={selectedSource === 3 || selectedSource === 1 ? "#6366f1" : "#475569"}
                    strokeWidth={selectedSource === 3 || selectedSource === 1 ? 2.5 : 1.5}
                    strokeDasharray={selectedSource === 3 ? "4 2" : "none"}
                    markerEnd={selectedSource === 3 || selectedSource === 1 ? "url(#arrow-active)" : "url(#arrow)"}
                    className="transition-colors duration-200"
                  />

                  {/* Edge: FlashAttention [3] -> Longformer [2] */}
                  <path
                    d="M 110 162 L 110 98"
                    fill="none"
                    stroke={selectedSource === 3 || selectedSource === 2 ? "#6366f1" : "#475569"}
                    strokeWidth={selectedSource === 3 || selectedSource === 2 ? 2.5 : 1.5}
                    markerEnd={selectedSource === 3 || selectedSource === 2 ? "url(#arrow-active)" : "url(#arrow)"}
                    className="transition-colors duration-200"
                  />

                  {/* Node 1: Attention Is All You Need (125k citations, Vaswani 2017) */}
                  <g
                    onClick={() => setSelectedSource(prev => prev === 1 ? null : 1)}
                    onMouseEnter={() => setHoveredNode(1)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer group"
                  >
                    {selectedSource === 1 && (
                      <circle cx="340" cy="130" r="42" fill="none" stroke="#6366f1" strokeWidth="2" strokeDasharray="3 3" />
                    )}
                    <circle
                      cx="340"
                      cy="130"
                      r="36"
                      fill="#18181b"
                      stroke={selectedSource === 1 ? "#6366f1" : "#10b981"}
                      strokeWidth={selectedSource === 1 ? 3 : 2}
                      className="group-hover:stroke-accent transition-all duration-200"
                    />
                    <text x="340" y="125" textAnchor="middle" fill="#f8fafc" fontSize="13" fontWeight="bold" fontFamily="monospace">
                      [1]
                    </text>
                    <text x="340" y="142" textAnchor="middle" fill="#94a3b8" fontSize="10">
                      2017
                    </text>
                    <text x="340" y="180" textAnchor="middle" fill="#e2e8f0" fontSize="11" fontWeight="500">
                      Vaswani et al.
                    </text>
                    <text x="340" y="195" textAnchor="middle" fill="#64748b" fontSize="10">
                      125k cites • 100%
                    </text>
                  </g>

                  {/* Node 2: Longformer (3.2k citations, Beltagy 2020) */}
                  <g
                    onClick={() => setSelectedSource(prev => prev === 2 ? null : 2)}
                    onMouseEnter={() => setHoveredNode(2)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer group"
                  >
                    {selectedSource === 2 && (
                      <circle cx="110" cy="70" r="30" fill="none" stroke="#6366f1" strokeWidth="2" strokeDasharray="3 3" />
                    )}
                    <circle
                      cx="110"
                      cy="70"
                      r="24"
                      fill="#18181b"
                      stroke={selectedSource === 2 ? "#6366f1" : "#10b981"}
                      strokeWidth={selectedSource === 2 ? 3 : 2}
                      className="group-hover:stroke-accent transition-all duration-200"
                    />
                    <text x="110" y="66" textAnchor="middle" fill="#f8fafc" fontSize="12" fontWeight="bold" fontFamily="monospace">
                      [2]
                    </text>
                    <text x="110" y="80" textAnchor="middle" fill="#94a3b8" fontSize="9">
                      2020
                    </text>
                    <text x="110" y="106" textAnchor="middle" fill="#e2e8f0" fontSize="11" fontWeight="500">
                      Longformer
                    </text>
                    <text x="110" y="119" textAnchor="middle" fill="#64748b" fontSize="10">
                      3.2k cites • 100%
                    </text>
                  </g>

                  {/* Node 3: FlashAttention (4.8k citations, Dao 2022) */}
                  <g
                    onClick={() => setSelectedSource(prev => prev === 3 ? null : 3)}
                    onMouseEnter={() => setHoveredNode(3)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer group"
                  >
                    {selectedSource === 3 && (
                      <circle cx="110" cy="190" r="32" fill="none" stroke="#6366f1" strokeWidth="2" strokeDasharray="3 3" />
                    )}
                    <circle
                      cx="110"
                      cy="190"
                      r="26"
                      fill="#18181b"
                      stroke={selectedSource === 3 ? "#6366f1" : "#f59e0b"}
                      strokeWidth={selectedSource === 3 ? 3 : 2}
                      className="group-hover:stroke-accent transition-all duration-200"
                    />
                    <text x="110" y="186" textAnchor="middle" fill="#f8fafc" fontSize="12" fontWeight="bold" fontFamily="monospace">
                      [3]
                    </text>
                    <text x="110" y="200" textAnchor="middle" fill="#94a3b8" fontSize="9">
                      2022
                    </text>
                    <text x="110" y="228" textAnchor="middle" fill="#e2e8f0" fontSize="11" fontWeight="500">
                      FlashAttention
                    </text>
                    <text x="110" y="241" textAnchor="middle" fill="#64748b" fontSize="10">
                      4.8k cites • 67%
                    </text>
                  </g>
                </svg>
              </div>

              {/* Dynamic Node Details Banner */}
              {(() => {
                const activeNum = hoveredNode || selectedSource || 1;
                const activePaper = papers.find(p => p.source_num === activeNum);
                if (!activePaper) return null;
                return (
                  <div className="p-3 rounded-lg bg-surface border border-border text-xs space-y-1.5 transition-all">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-accent">Source [{activePaper.source_num}]</span>
                      <span className="font-mono text-text-tertiary">{activePaper.year} • {activePaper.venue}</span>
                    </div>
                    <div className="font-medium text-text-primary text-xs line-clamp-1">{activePaper.title}</div>
                    <div className="flex items-center justify-between text-[11px] text-text-secondary pt-1 border-t border-border/50">
                      <span>{activePaper.citation_count.toLocaleString()} citations</span>
                      <span className="font-semibold text-success">
                        {activePaper.support_rate ? `${Math.round(activePaper.support_rate * 100)}% Verified Support` : "100% Verified"}
                      </span>
                    </div>
                  </div>
                );
              })()}

              {/* Topology Legend */}
              <div className="flex items-center justify-between text-[11px] text-text-tertiary px-1 pt-1 border-t border-border">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> ≥80% Support
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> Partial
                </span>
                <span className="flex items-center gap-1">
                  <span className="font-mono text-text-secondary">A → B</span> Cites
                </span>
              </div>
            </Card>
          )}

          {activeTab === "sources" && (
            <div className="space-y-3 sticky top-20">
              {papers.map((p) => (
                <Card key={p.source_num} className="p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-accent">Source [{p.source_num}]</span>
                    <Badge variant={p.support_rate && p.support_rate >= 0.8 ? "supported" : "partial"}>
                      {p.support_rate ? `${Math.round(p.support_rate * 100)}% verified` : "Unverified"}
                    </Badge>
                  </div>
                  <h4 className="text-xs font-semibold text-text-primary">{p.title}</h4>
                  <p className="text-[11px] text-text-secondary line-clamp-3 leading-relaxed">
                    {p.abstract}
                  </p>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
