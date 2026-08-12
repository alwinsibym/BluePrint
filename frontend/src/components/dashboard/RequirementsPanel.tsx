import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Loader2, ChevronDown, ChevronUp, RefreshCw, Sparkles, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { createRequirements, type RequirementsResponse } from "@/services/requirements";

// ──────────────────────────────────────────────
// Sub-components
// ──────────────────────────────────────────────

interface AccordionSectionProps {
  title: string;
  badge?: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function AccordionSection({ title, badge, children, defaultOpen = false }: AccordionSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 bg-muted/40 hover:bg-muted/70 transition-colors text-sm font-medium text-foreground"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2">
          {title}
          {badge !== undefined && (
            <span className="inline-flex items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-semibold px-1.5 py-0.5 min-w-[20px]">
              {badge}
            </span>
          )}
        </span>
        {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
      </button>
      {open && <div className="px-4 py-3 bg-card text-sm text-foreground">{children}</div>}
    </div>
  );
}

function BulletList({ items }: { items: string[] }) {
  if (!items.length) return <p className="text-muted-foreground italic text-xs">None provided.</p>;
  return (
    <ul className="list-disc list-inside space-y-1">
      {items.map((item, i) => (
        <li key={i} className="text-sm leading-snug">{item}</li>
      ))}
    </ul>
  );
}

function TechStackGrid({ stack }: { stack: RequirementsResponse["recommended_tech_stack"] }) {
  const entries = [
    { label: "Frontend", value: stack.frontend },
    { label: "Backend", value: stack.backend },
    { label: "Database", value: stack.database },
    { label: "AI Framework", value: stack.ai_framework },
  ];
  return (
    <div className="grid grid-cols-2 gap-2">
      {entries.map(({ label, value }) => (
        <div key={label} className="rounded-md border border-border bg-muted/30 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground font-medium">{label}</p>
          <p className="text-sm font-semibold text-foreground mt-0.5">{value}</p>
        </div>
      ))}
    </div>
  );
}

function UserStoriesTable({ stories }: { stories: RequirementsResponse["user_stories"] }) {
  if (!stories.length) return <p className="text-muted-foreground italic text-xs">No user stories generated.</p>;
  return (
    <div className="space-y-2">
      {stories.map((s, i) => (
        <div key={i} className="rounded-md border border-border bg-muted/20 px-3 py-2 text-sm">
          <p><span className="font-medium text-primary">As a</span> {s.role},</p>
          <p><span className="font-medium">I want to</span> {s.desire}</p>
          <p><span className="font-medium text-success">so that</span> {s.benefit}.</p>
        </div>
      ))}
    </div>
  );
}

function RequirementsResult({ data }: { data: RequirementsResponse }) {
  return (
    <div className="space-y-2 mt-4">
      {/* Header summary */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 px-4 py-3">
        <h2 className="font-semibold text-base text-foreground">{data.project_name}</h2>
        <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{data.project_overview}</p>
      </div>

      <AccordionSection title="Objectives" badge={data.objectives.length} defaultOpen>
        <BulletList items={data.objectives} />
      </AccordionSection>

      <AccordionSection title="Functional Requirements" badge={data.functional_requirements.length}>
        <BulletList items={data.functional_requirements} />
      </AccordionSection>

      <AccordionSection title="Non-Functional Requirements" badge={data.non_functional_requirements.length}>
        <BulletList items={data.non_functional_requirements} />
      </AccordionSection>

      <AccordionSection title="User Roles" badge={data.user_roles.length}>
        <BulletList items={data.user_roles} />
      </AccordionSection>

      <AccordionSection title="User Stories" badge={data.user_stories.length}>
        <UserStoriesTable stories={data.user_stories} />
      </AccordionSection>

      <AccordionSection title="Suggested Modules" badge={data.suggested_modules.length}>
        <BulletList items={data.suggested_modules} />
      </AccordionSection>

      <AccordionSection title="Recommended Tech Stack">
        <TechStackGrid stack={data.recommended_tech_stack} />
      </AccordionSection>

      <AccordionSection title="Assumptions" badge={data.assumptions.length}>
        <BulletList items={data.assumptions} />
      </AccordionSection>

      <AccordionSection title="Constraints" badge={data.constraints.length}>
        <BulletList items={data.constraints} />
      </AccordionSection>

      <AccordionSection title="Future Scope" badge={data.future_scope.length}>
        <BulletList items={data.future_scope} />
      </AccordionSection>
    </div>
  );
}

// ──────────────────────────────────────────────
// Main panel
// ──────────────────────────────────────────────

export function RequirementsPanel({ 
  initialIdea,
  requirements: initialRequirements,
  onRequirementsGenerated 
}: { 
  initialIdea?: string | null;
  requirements?: RequirementsResponse | null;
  onRequirementsGenerated?: (data: RequirementsResponse) => void;
}) {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RequirementsResponse | null>(initialRequirements ?? null);
  const [error, setError] = useState<string | null>(null);
  const [lastIdea, setLastIdea] = useState("");
  const [showEditForm, setShowEditForm] = useState(false);

  useEffect(() => {
    if (initialRequirements) {
      setResult(initialRequirements);
    }
  }, [initialRequirements]);

  const handleGenerate = async (ideaToUse?: string) => {
    const input = (ideaToUse ?? idea).trim();
    if (!input) {
      toast.error("Please describe your project idea first.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setLastIdea(input);

    try {
      const data = await createRequirements(input);
      setResult(data);
      setShowEditForm(false);
      if (onRequirementsGenerated) onRequirementsGenerated(data);
      toast.success("Requirements document generated!");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err instanceof Error ? err.message : "Unknown error");
      setError(msg);
      toast.error("Failed to generate requirements.");
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => handleGenerate(lastIdea);

  // Auto-generate if initialIdea is provided from the main dashboard form
  useEffect(() => {
    if (initialIdea && initialIdea.trim() !== "" && initialIdea !== lastIdea) {
      setIdea(initialIdea);
      handleGenerate(initialIdea);
    }
  }, [initialIdea]);

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Sparkles className="h-5 w-5 text-primary" />
              Requirements Agent
            </CardTitle>
            <CardDescription>
              Structured primary planning document generated from project idea.
            </CardDescription>
          </div>
          {result && !loading && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowEditForm(!showEditForm)}
            >
              {showEditForm ? "Hide Form" : "Re-generate Requirements"}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Input area — shown if no result yet, or if user clicks Re-generate */}
        {(!result || showEditForm) && (
          <div className="space-y-4 rounded-lg border border-border bg-muted/20 p-4">
            <div className="space-y-2">
              <label htmlFor="req-idea-textarea" className="text-sm font-medium text-foreground">
                Project Idea
              </label>
              <Textarea
                id="req-idea-textarea"
                placeholder="e.g. A web app for personal budgeting with charts, CSV export, and AI-powered spending insights..."
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
                rows={4}
                disabled={loading}
                className="resize-none bg-background"
              />
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                id="req-generate-btn"
                onClick={() => handleGenerate()}
                disabled={loading || !idea.trim()}
                className="gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating…
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Generate Requirements
                  </>
                )}
              </Button>

              {error && (
                <Button
                  id="req-retry-btn"
                  variant="outline"
                  onClick={handleRetry}
                  disabled={loading}
                  className="gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-2 mt-4 animate-pulse">
            <p className="text-xs text-muted-foreground animate-pulse mb-2">Analyzing requirements & user stories…</p>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 rounded-lg bg-muted/60" />
            ))}
          </div>
        )}

        {/* Result */}
        {result && !loading && <RequirementsResult data={result} />}
      </CardContent>
    </Card>
  );
}
