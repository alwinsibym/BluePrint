import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Loader2, ChevronDown, ChevronUp, RefreshCw, Sparkles, AlertCircle, Edit3, Save, Plus, Trash, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { createRequirements, type RequirementsResponse, type UserStory } from "@/services/requirements";

// ──────────────────────────────────────────────
// Sub-components for display
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
    <div className="border border-border rounded-lg overflow-hidden mb-2">
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
    { label: "Frontend Client", value: stack.frontend },
    { label: "Backend Application", value: stack.backend },
    { label: "Database Server", value: stack.database },
    { label: "Inference Engine", value: stack.ai_framework },
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

function UserStoriesTable({ stories }: { stories: UserStory[] }) {
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

// ──────────────────────────────────────────────
// Main panel component
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

  // Interactive editing states
  const [isEditing, setIsEditing] = useState(false);
  const [editOverview, setEditOverview] = useState("");
  const [editObjectives, setEditObjectives] = useState<string[]>([]);
  const [editFunc, setEditFunc] = useState<string[]>([]);
  const [editNonFunc, setEditNonFunc] = useState<string[]>([]);
  const [editRoles, setEditRoles] = useState<string[]>([]);
  const [editStories, setEditStories] = useState<UserStory[]>([]);
  const [editStack, setEditStack] = useState<RequirementsResponse["recommended_tech_stack"]>({
    frontend: "",
    backend: "",
    database: "",
    ai_framework: ""
  });

  // Sync state if initialRequirements updates
  useEffect(() => {
    if (initialRequirements) {
      setResult(initialRequirements);
    }
  }, [initialRequirements]);

  // Load editing state
  const startEditing = () => {
    if (!result) return;
    setEditOverview(result.project_overview || "");
    setEditObjectives([...(result.objectives || [])]);
    setEditFunc([...(result.functional_requirements || [])]);
    setEditNonFunc([...(result.non_functional_requirements || [])]);
    setEditRoles([...(result.user_roles || [])]);
    setEditStories([...(result.user_stories || [])]);
    setEditStack({ ...(result.recommended_tech_stack || { frontend: "", backend: "", database: "", ai_framework: "" }) });
    setIsEditing(true);
  };

  const saveEdits = () => {
    if (!result) return;
    const updated: RequirementsResponse = {
      ...result,
      project_overview: editOverview,
      objectives: editObjectives,
      functional_requirements: editFunc,
      non_functional_requirements: editNonFunc,
      user_roles: editRoles,
      user_stories: editStories,
      recommended_tech_stack: editStack,
    };
    setResult(updated);
    setIsEditing(false);
    if (onRequirementsGenerated) onRequirementsGenerated(updated);
    toast.success("Requirements refined and validated by developer!");
  };

  // Helper arrays update functions
  const addBullet = (setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter(prev => [...prev, "New requirement specification"]);
  };

  const updateBullet = (idx: number, val: string, setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter(prev => prev.map((item, i) => i === idx ? val : item));
  };

  const removeBullet = (idx: number, setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter(prev => prev.filter((_, i) => i !== idx));
  };

  const addUserStory = () => {
    setEditStories(prev => [...prev, { role: "User", desire: "do action", benefit: "get result" }]);
  };

  const updateUserStory = (idx: number, key: keyof UserStory, val: string) => {
    setEditStories(prev => prev.map((story, i) => i === idx ? { ...story, [key]: val } : story));
  };

  const removeUserStory = (idx: number) => {
    setEditStories(prev => prev.filter((_, i) => i !== idx));
  };

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

  useEffect(() => {
    if (initialIdea && initialIdea.trim() !== "" && initialIdea !== lastIdea) {
      setIdea(initialIdea);
      handleGenerate(initialIdea);
    }
  }, [initialIdea]);

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-3 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Sparkles className="h-5 w-5 text-primary" />
              Requirements Specification (IEEE Std 830)
            </CardTitle>
            <CardDescription>
              Interactive requirements refinement panel. Edit to eliminate AI hallucinations.
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {result && !loading && !isEditing && (
              <Button variant="outline" size="sm" onClick={startEditing} className="gap-1 text-primary">
                <Edit3 className="h-3.5 w-3.5" /> Refine Specs
              </Button>
            )}
            {result && !loading && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEditForm(!showEditForm)}
              >
                {showEditForm ? "Hide Form" : "Re-generate"}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {/* Input area */}
        {(!result || showEditForm) && (
          <div className="space-y-4 rounded-lg border border-border bg-muted/20 p-4">
            <div className="space-y-2">
              <label htmlFor="req-idea-textarea" className="text-sm font-medium text-foreground">
                Describe your project idea in detail:
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

        {/* ─── INTERACTIVE EDITOR ─── */}
        {result && isEditing && (
          <div className="space-y-4 border border-brand/30 bg-brand/5 rounded-xl p-4 mt-4">
            <div className="flex items-center justify-between border-b border-brand/20 pb-2 mb-4">
              <span className="text-sm font-semibold text-brand">Refining Project Requirements</span>
              <Button size="sm" onClick={saveEdits} className="gap-1 bg-emerald-600 hover:bg-emerald-700 text-white">
                <Check className="h-4 w-4" /> Approve & Save
              </Button>
            </div>

            {/* Overview */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Project Scope & Overview</label>
              <Textarea
                value={editOverview}
                onChange={(e) => setEditOverview(e.target.value)}
                rows={4}
                className="bg-background"
              />
            </div>

            {/* Functional Requirements */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Functional Requirements</label>
                <Button variant="ghost" size="sm" onClick={() => addBullet(setEditFunc)} className="h-6 gap-1 text-primary text-xs">
                  <Plus className="h-3 w-3" /> Add Row
                </Button>
              </div>
              <div className="space-y-1.5">
                {editFunc.map((f, i) => (
                  <div key={i} className="flex gap-2">
                    <Input value={f} onChange={(e) => updateBullet(i, e.target.value, setEditFunc)} className="bg-background h-8" />
                    <Button variant="ghost" size="icon" onClick={() => removeBullet(i, setEditFunc)} className="h-8 w-8 text-destructive hover:bg-destructive/10">
                      <Trash className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Non-Functional Requirements */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Non-Functional Requirements</label>
                <Button variant="ghost" size="sm" onClick={() => addBullet(setEditNonFunc)} className="h-6 gap-1 text-primary text-xs">
                  <Plus className="h-3 w-3" /> Add Row
                </Button>
              </div>
              <div className="space-y-1.5">
                {editNonFunc.map((nf, i) => (
                  <div key={i} className="flex gap-2">
                    <Input value={nf} onChange={(e) => updateBullet(i, e.target.value, setEditNonFunc)} className="bg-background h-8" />
                    <Button variant="ghost" size="icon" onClick={() => removeBullet(i, setEditNonFunc)} className="h-8 w-8 text-destructive hover:bg-destructive/10">
                      <Trash className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Tech Stack */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Technology Profile</label>
              <div className="grid grid-cols-2 gap-2 bg-background p-3 rounded-lg border">
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase font-medium">Frontend</span>
                  <Input value={editStack.frontend} onChange={(e) => setEditStack(prev => ({ ...prev, frontend: e.target.value }))} className="h-8 mt-1" />
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase font-medium">Backend</span>
                  <Input value={editStack.backend} onChange={(e) => setEditStack(prev => ({ ...prev, backend: e.target.value }))} className="h-8 mt-1" />
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase font-medium">Database</span>
                  <Input value={editStack.database} onChange={(e) => setEditStack(prev => ({ ...prev, database: e.target.value }))} className="h-8 mt-1" />
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground uppercase font-medium">Inference</span>
                  <Input value={editStack.ai_framework} onChange={(e) => setEditStack(prev => ({ ...prev, ai_framework: e.target.value }))} className="h-8 mt-1" />
                </div>
              </div>
            </div>

            {/* User Stories */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">User Stories</label>
                <Button variant="ghost" size="sm" onClick={addUserStory} className="h-6 gap-1 text-primary text-xs">
                  <Plus className="h-3 w-3" /> Add Use Case
                </Button>
              </div>
              <div className="space-y-2">
                {editStories.map((story, i) => (
                  <div key={i} className="flex flex-col gap-1.5 bg-background p-2.5 rounded-lg border border-border">
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground font-medium">As a</span>
                      <Input value={story.role} onChange={(e) => updateUserStory(i, "role", e.target.value)} className="h-7 text-xs flex-1" />
                      <Button variant="ghost" size="icon" onClick={() => removeUserStory(i)} className="h-7 w-7 text-destructive hover:bg-destructive/10">
                        <Trash className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground font-medium">I want to</span>
                      <Input value={story.desire} onChange={(e) => updateUserStory(i, "desire", e.target.value)} className="h-7 text-xs flex-1" />
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground font-medium">so that</span>
                      <Input value={story.benefit} onChange={(e) => updateUserStory(i, "benefit", e.target.value)} className="h-7 text-xs flex-1" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
              <Button size="sm" onClick={saveEdits} className="gap-1 bg-emerald-600 hover:bg-emerald-700 text-white">
                <Check className="h-4 w-4" /> Save Specifications
              </Button>
            </div>
          </div>
        )}

        {/* ─── DISPLAY RESULT ─── */}
        {result && !loading && !isEditing && (
          <div className="space-y-4">
            <div className="rounded-xl border border-primary/20 bg-primary/5 px-4 py-3">
              <h2 className="font-semibold text-base text-foreground">{result.project_name}</h2>
              <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{result.project_overview}</p>
            </div>

            <AccordionSection title="Objectives" badge={result.objectives?.length} defaultOpen>
              <BulletList items={result.objectives || []} />
            </AccordionSection>

            <AccordionSection title="Functional Requirements" badge={result.functional_requirements?.length} defaultOpen>
              <BulletList items={result.functional_requirements || []} />
            </AccordionSection>

            <AccordionSection title="Non-Functional Requirements" badge={result.non_functional_requirements?.length}>
              <BulletList items={result.non_functional_requirements || []} />
            </AccordionSection>

            <AccordionSection title="User Roles" badge={result.user_roles?.length}>
              <BulletList items={result.user_roles || []} />
            </AccordionSection>

            <AccordionSection title="User Stories" badge={result.user_stories?.length}>
              <UserStoriesTable stories={result.user_stories || []} />
            </AccordionSection>

            <AccordionSection title="Suggested Modules" badge={result.suggested_modules?.length}>
              <BulletList items={result.suggested_modules || []} />
            </AccordionSection>

            <AccordionSection title="Recommended Tech Stack">
              <TechStackGrid stack={result.recommended_tech_stack} />
            </AccordionSection>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
