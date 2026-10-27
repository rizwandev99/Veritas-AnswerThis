"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { IconButton } from "@/components/ui/IconButton";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { Tooltip } from "@/components/ui/Tooltip";
import { ProgressStepper } from "@/components/ui/ProgressStepper";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Search, Sparkles, BookOpen, ExternalLink, Check, AlertTriangle, XCircle, HelpCircle } from "lucide-react";

export default function DesignSystemGallery() {
  const [activeStep, setActiveStep] = useState(2);

  const steps = [
    { id: "search", label: "Searching papers" },
    { id: "read", label: "Reading abstracts" },
    { id: "synthesize", label: "Synthesizing review" },
    { id: "verify", label: "Verifying citations" },
  ];

  return (
    <div className="min-h-screen bg-background text-text-primary p-6 md:p-12 transition-colors duration-150">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight">Veritas</span>
              <Badge variant="outline">Design System</Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Linear-grade semantic design tokens, components, and verification badges.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-text-tertiary">Toggle Theme:</span>
            <ThemeToggle />
          </div>
        </div>

        {/* 1. Buttons */}
        <section className="space-y-4">
          <h2 className="text-base font-semibold tracking-tight text-text-primary">1. Buttons & Controls</h2>
          <div className="flex flex-wrap items-center gap-3 p-6 rounded-lg bg-surface border border-border">
            <Button variant="primary">Primary Action</Button>
            <Button variant="secondary">Secondary Action</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
            <Button variant="primary" loading>Loading...</Button>
            <IconButton aria-label="Search" variant="outline"><Search className="w-4 h-4" /></IconButton>
            <IconButton aria-label="Sparkles" variant="secondary"><Sparkles className="w-4 h-4" /></IconButton>
          </div>
        </section>

        {/* 2. Form Inputs */}
        <section className="space-y-4">
          <h2 className="text-base font-semibold tracking-tight text-text-primary">2. Form Inputs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6 rounded-lg bg-surface border border-border">
            <Input placeholder="Search research topics (e.g. CRISPR off-target effects)..." icon={<Search className="w-4 h-4" />} />
            <Input defaultValue="Pre-filled query value" />
            <Input placeholder="Disabled input" disabled />
          </div>
        </section>

        {/* 3. Academic Verification Badges */}
        <section className="space-y-4">
          <h2 className="text-base font-semibold tracking-tight text-text-primary">3. Verification Badges (Claim Status)</h2>
          <div className="flex flex-wrap items-center gap-4 p-6 rounded-lg bg-surface border border-border">
            <Tooltip content="Claim is directly confirmed by cited abstract text.">
              <Badge variant="supported" interactive>
                <Check className="w-3 h-3 text-success" /> Supported (98%)
              </Badge>
            </Tooltip>
            <Tooltip content="Claim is partially entailed or context-dependent.">
              <Badge variant="partial" interactive>
                <AlertTriangle className="w-3 h-3 text-warning" /> Partial (65%)
              </Badge>
            </Tooltip>
            <Tooltip content="Claim contradicts or is not found in cited abstract.">
              <Badge variant="unsupported" interactive>
                <XCircle className="w-3 h-3 text-danger" /> Unsupported
              </Badge>
            </Tooltip>
            <Tooltip content="Verification pending completion.">
              <Badge variant="unchecked">
                <HelpCircle className="w-3 h-3 text-text-tertiary" /> Checking...
              </Badge>
            </Tooltip>
            <Badge variant="info">OpenAlex</Badge>
            <Badge variant="outline">DOI 10.1038/s41586</Badge>
          </div>
        </section>

        {/* 4. Progress Stepper */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold tracking-tight text-text-primary">4. Pipeline Progress Stepper</h2>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" onClick={() => setActiveStep((s) => Math.max(0, s - 1))}>Prev</Button>
              <Button size="sm" variant="outline" onClick={() => setActiveStep((s) => Math.min(steps.length, s + 1))}>Next</Button>
            </div>
          </div>
          <div className="p-6 rounded-lg bg-surface border border-border">
            <ProgressStepper steps={steps} currentStepIndex={activeStep} />
          </div>
        </section>

        {/* 5. Cards & High-Density Academic Containers */}
        <section className="space-y-4">
          <h2 className="text-base font-semibold tracking-tight text-text-primary">5. Cards & Containers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-5 space-y-3">
              <div className="flex items-start justify-between">
                <span className="text-xs font-mono text-accent">[1] Vaswani et al., 2017</span>
                <Badge variant="supported">Supported</Badge>
              </div>
              <h3 className="text-sm font-semibold text-text-primary">Attention Is All You Need</h3>
              <p className="text-xs text-text-secondary leading-relaxed line-clamp-3">
                The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer, based solely on attention mechanisms.
              </p>
              <div className="flex items-center justify-between pt-2 text-xs text-text-tertiary border-t border-border">
                <span>Citations: 120,400</span>
                <span className="inline-flex items-center gap-1 hover:text-text-primary cursor-pointer">
                  View Source <ExternalLink className="w-3 h-3" />
                </span>
              </div>
            </Card>

            <Card elevated className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-text-secondary">Verification Evidence</span>
                <span className="text-xs font-mono text-success">Cosine: 0.89</span>
              </div>
              <p className="text-xs text-text-primary bg-surface p-3 rounded border border-border font-mono leading-relaxed">
                "...multi-head attention allows the model to jointly attend to information from different representation subspaces..."
              </p>
              <div className="text-xs text-text-tertiary">
                Exact substring match confirmed in abstract chunk #2.
              </div>
            </Card>
          </div>
        </section>

        {/* 6. Tabs & Skeletons */}
        <section className="space-y-4">
          <h2 className="text-base font-semibold tracking-tight text-text-primary">6. Tabs & Skeleton States</h2>
          <Card className="p-6">
            <Tabs defaultValue="review">
              <TabsList>
                <TabsTrigger value="review">Review</TabsTrigger>
                <TabsTrigger value="graph">Citation Graph</TabsTrigger>
                <TabsTrigger value="sources">Sources (12)</TabsTrigger>
              </TabsList>
              <TabsContent value="review">
                <div className="space-y-2.5 pt-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              </TabsContent>
              <TabsContent value="graph">
                <div className="h-32 flex items-center justify-center text-xs text-text-tertiary border border-dashed border-border rounded-md">
                  Interactive Node-Link Canvas
                </div>
              </TabsContent>
              <TabsContent value="sources">
                <div className="space-y-2 pt-2">
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-8 w-full" />
                </div>
              </TabsContent>
            </Tabs>
          </Card>
        </section>
      </div>
    </div>
  );
}
