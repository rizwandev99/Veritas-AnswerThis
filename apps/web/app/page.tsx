"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Search, Sparkles, ArrowRight, CheckCircle2, ShieldCheck, Network, Terminal } from "lucide-react";

const EXAMPLE_QUERIES = [
  { id: "ex-1", query: "Transformer self-attention efficiency in long contexts", papers: 12, score: 92 },
  { id: "ex-2", query: "CRISPR-Cas9 off-target mutation mitigation mechanisms", papers: 10, score: 88 },
  { id: "ex-3", query: "GLP-1 receptor agonists and cardiovascular mortality", papers: 14, score: 95 },
  { id: "ex-4", query: "Surface code quantum error correction physical thresholds", papers: 8, score: 84 },
  { id: "ex-5", query: "Carbon tax effectiveness on aggregate industrial emissions", papers: 11, score: 90 },
];

export default function LandingPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      // Create review request to backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() }),
      });
      if (res.ok) {
        const data = await res.json();
        router.push(`/r/${data.id}`);
      } else {
        // Fallback for demonstration / mock
        const mockId = "rev_" + Math.random().toString(36).substring(2, 9);
        router.push(`/r/${mockId}?q=${encodeURIComponent(query.trim())}`);
      }
    } catch {
      const mockId = "rev_" + Math.random().toString(36).substring(2, 9);
      router.push(`/r/${mockId}?q=${encodeURIComponent(query.trim())}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-text-primary flex flex-col justify-between selection:bg-accent selection:text-white">
      {/* Navbar */}
      <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-bold tracking-tight text-base flex items-center gap-1.5">
              <ShieldCheck className="w-5 h-5 text-accent" /> Veritas
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-accent-muted text-accent font-medium hidden sm:inline-block">
              Citation-Verified AI
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/design" className="text-xs text-text-secondary hover:text-text-primary transition-colors">
              Design System
            </Link>
            <div className="h-4 w-px bg-border" />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-4xl mx-auto px-4 py-16 sm:py-24 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-elevated border border-border text-xs text-text-secondary mb-8 animate-fade-in">
          <Sparkles className="w-3.5 h-3.5 text-accent" />
          <span>Grounded in peer-reviewed abstracts with claim verification</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-text-primary max-w-3xl leading-[1.15]">
          Generate literature reviews where <span className="text-accent underline decoration-accent/40 underline-offset-4">every claim is verified</span>.
        </h1>

        <p className="mt-4 text-base sm:text-lg text-text-secondary max-w-2xl leading-relaxed">
          Ask any research question. Veritas searches real papers, generates a structured review, and audits every sentence against source abstracts for factual entailment.
        </p>

        {/* Search Box */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mt-10">
          <div className="flex flex-col sm:flex-row items-center gap-2 p-1.5 rounded-lg bg-surface border border-border-strong shadow-lg focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20 transition-all">
            <div className="flex items-center w-full pl-3 pr-2">
              <Search className="w-5 h-5 text-text-tertiary shrink-0 mr-2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type a research question (e.g. quantum error correction thresholds)..."
                className="w-full h-11 bg-transparent text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none"
              />
            </div>
            <Button
              type="submit"
              size="md"
              loading={isSubmitting}
              className="w-full sm:w-auto shrink-0 h-10 px-5 shadow-sm"
            >
              Generate Review <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <div className="flex items-center justify-between mt-2.5 px-2 text-xs text-text-tertiary">
            <span>Press <kbd className="px-1.5 py-0.5 rounded bg-surface-elevated border border-border font-mono text-[10px]">Enter</kbd> to generate</span>
            <span className="flex items-center gap-1">
              <Terminal className="w-3 h-3" /> <kbd className="px-1.5 py-0.5 rounded bg-surface-elevated border border-border font-mono text-[10px]">Cmd+K</kbd> for palette
            </span>
          </div>
        </form>

        {/* Example Query Chips */}
        <div className="w-full max-w-2xl mt-8">
          <div className="text-xs font-semibold text-text-tertiary uppercase tracking-wider text-left mb-3">
            Or try an example query
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((ex) => (
              <button
                key={ex.id}
                type="button"
                onClick={() => setQuery(ex.query)}
                className="text-xs text-left px-3 py-1.5 rounded-md bg-surface-elevated border border-border hover:border-accent/60 hover:text-accent transition-all text-text-secondary select-none"
              >
                {ex.query}
              </button>
            ))}
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-4xl mt-16 text-left">
          <Card className="p-5 space-y-2">
            <div className="w-8 h-8 rounded bg-success-surface border border-success-border flex items-center justify-center text-success mb-3">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary">Claim Verification</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Every factual sentence is verified against candidate abstracts, scored as Supported, Partial, or Unsupported.
            </p>
          </Card>

          <Card className="p-5 space-y-2">
            <div className="w-8 h-8 rounded bg-info-surface border border-info-border flex items-center justify-center text-info mb-3">
              <Network className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary">Citation Graph</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Interactive topological network visualizes cross-paper citation links and claim support density per paper.
            </p>
          </Card>

          <Card className="p-5 space-y-2">
            <div className="w-8 h-8 rounded bg-surface-elevated border border-border flex items-center justify-center text-text-primary mb-3">
              <ShieldCheck className="w-4 h-4 text-accent" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary">Verbatim Grounding</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Inspect exact matched substrings inside source abstracts with full confidence scores and BibTeX export.
            </p>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 text-center text-xs text-text-tertiary">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Veritas — Built for AnswerThis showcase</span>
          <div className="flex items-center gap-4">
            <Link href="https://openalex.org" target="_blank" className="hover:text-text-primary transition-colors">
              OpenAlex Data
            </Link>
            <span>•</span>
            <Link href="/design" className="hover:text-text-primary transition-colors">
              Design Tokens
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
