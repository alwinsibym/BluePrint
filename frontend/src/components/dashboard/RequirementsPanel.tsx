import { useState, useEffect, useRef } from "react";
import { toast } from "sonner";
import {
  Loader2, ChevronDown, ChevronUp, Sparkles, AlertCircle,
  Edit3, Plus, Trash, Check, MessageSquare, Zap, ArrowRight,
  CheckCircle2, Clock, ChevronRight, User, Bot, RotateCcw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { createRequirements, type RequirementsResponse, type UserStory } from "@/services/requirements";
import {
  startElicitation, sendElicitationAnswer,
  type ElicitationMessage, type ElicitationResponse,
} from "@/services/elicitation";

// ── Constants ──────────────────────────────────────────────────────────────────
const PHASES = [
  { label: "Stakeholders & Context",       icon: "👥" },
  { label: "Goals & Success Criteria",     icon: "🎯" },
  { label: "Core Features & Workflows",    icon: "⚙️" },
  { label: "System Boundaries",            icon: "🔲" },
  { label: "Quality & Constraints",        icon: "📊" },
  { label: "Edge Cases & Risks",           icon: "⚠️" },
];

// ── Sub-components ─────────────────────────────────────────────────────────────
function AccordionSection({
  title, badge, children, defaultOpen = false,
}: { title: string; badge?: number; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-border rounded-lg overflow-hidden mb-2">
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
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
      {items.map((item, i) => <li key={i} className="text-sm leading-snug">{item}</li>)}
    </ul>
  );
}

function TechStackGrid({ stack }: { stack: RequirementsResponse["recommended_tech_stack"] }) {
  const entries = [
    { label: "Frontend", value: stack.frontend },
    { label: "Backend", value: stack.backend },
    { label: "Database", value: stack.database },
    { label: "AI Engine", value: stack.ai_framework },
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

// ── Phase progress bar ─────────────────────────────────────────────────────────
function PhaseProgress({ currentPhase, progress }: { currentPhase: number; progress: number }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="font-medium">Elicitation Progress</span>
        <span>{progress}%</span>
      </div>
      <Progress value={progress} className="h-2" />
      <div className="flex gap-1.5 flex-wrap">
        {PHASES.map((phase, i) => (
          <div
            key={i}
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-medium transition-all ${
              i + 1 < currentPhase
                ? "bg-emerald-500/15 text-emerald-600 border border-emerald-500/30"
                : i + 1 === currentPhase
                ? "bg-primary/15 text-primary border border-primary/30"
                : "bg-muted/40 text-muted-foreground border border-border"
            }`}
          >
            <span>{phase.icon}</span>
            <span className="hidden sm:inline">{phase.label.split(" ")[0]}</span>
            {i + 1 < currentPhase && <CheckCircle2 className="h-2.5 w-2.5" />}
            {i + 1 === currentPhase && <Clock className="h-2.5 w-2.5" />}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Chat bubble ────────────────────────────────────────────────────────────────
function ChatBubble({ msg, isLatest }: { msg: ElicitationMessage; isLatest: boolean }) {
  const isBot = msg.role === "assistant";
  return (
    <div className={`flex gap-2.5 ${isBot ? "items-start" : "items-start flex-row-reverse"} ${isLatest ? "animate-in fade-in slide-in-from-bottom-2 duration-300" : ""}`}>
      <div className={`shrink-0 flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
        isBot ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground border border-border"
      }`}>
        {isBot ? <Bot className="h-3.5 w-3.5" /> : <User className="h-3.5 w-3.5" />}
      </div>
      <div className={`max-w-[82%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
        isBot
          ? "bg-primary/8 border border-primary/15 text-foreground rounded-tl-sm"
          : "bg-muted/60 border border-border text-foreground rounded-tr-sm"
      }`}>
        {isBot && (
          <p className="text-[9px] font-semibold uppercase tracking-widest text-primary/70 mb-1">
            Requirements Analyst • Phase {msg.phase}
          </p>
        )}
        <p>{msg.content}</p>
      </div>
    </div>
  );
}

// ── Edit form ──────────────────────────────────────────────────────────────────
function RequirementsEditForm({
  result, onSave, onCancel,
}: {
  result: RequirementsResponse;
  onSave: (r: RequirementsResponse) => void;
  onCancel: () => void;
}) {
  const [editOverview, setEditOverview] = useState(result.project_overview || "");
  const [editFunc, setEditFunc] = useState<string[]>([...(result.functional_requirements || [])]);
  const [editNonFunc, setEditNonFunc] = useState<string[]>([...(result.non_functional_requirements || [])]);
  const [editRoles, setEditRoles] = useState<string[]>([...(result.user_roles || [])]);
  const [editStories, setEditStories] = useState<UserStory[]>([...(result.user_stories || [])]);
  const [editStack, setEditStack] = useState({ ...(result.recommended_tech_stack) });

  const addBullet = (setter: React.Dispatch<React.SetStateAction<string[]>>) =>
    setter(p => [...p, ""]);
  const updBullet = (i: number, v: string, setter: React.Dispatch<React.SetStateAction<string[]>>) =>
    setter(p => p.map((x, j) => j === i ? v : x));
  const delBullet = (i: number, setter: React.Dispatch<React.SetStateAction<string[]>>) =>
    setter(p => p.filter((_, j) => j !== i));

  const handleSave = () => {
    onSave({
      ...result,
      project_overview: editOverview,
      functional_requirements: editFunc.filter(Boolean),
      non_functional_requirements: editNonFunc.filter(Boolean),
      user_roles: editRoles.filter(Boolean),
      user_stories: editStories,
      recommended_tech_stack: editStack,
    });
  };

  const EditableList = ({
    label, items, setter,
  }: { label: string; items: string[]; setter: React.Dispatch<React.SetStateAction<string[]>> }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</label>
        <Button variant="ghost" size="sm" onClick={() => addBullet(setter)} className="h-6 gap-1 text-primary text-xs">
          <Plus className="h-3 w-3" /> Add
        </Button>
      </div>
      <div className="space-y-1.5">
        {items.map((f, i) => (
          <div key={i} className="flex gap-2">
            <Input value={f} onChange={e => updBullet(i, e.target.value, setter)} className="bg-background h-8 text-sm" placeholder="Enter requirement..." />
            <Button variant="ghost" size="icon" onClick={() => delBullet(i, setter)} className="h-8 w-8 text-destructive hover:bg-destructive/10 shrink-0">
              <Trash className="h-3.5 w-3.5" />
            </Button>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-xs text-muted-foreground italic pl-1">No items yet. Click Add to create one.</p>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-5 border border-emerald-500/30 bg-emerald-500/5 rounded-xl p-4">
      <div className="flex items-center justify-between border-b border-emerald-500/20 pb-3">
        <div>
          <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">Review & Refine Requirements</p>
          <p className="text-xs text-muted-foreground mt-0.5">These were synthesised from your interview. Edit freely before approving.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onCancel}>Cancel</Button>
          <Button size="sm" onClick={handleSave} className="gap-1 bg-emerald-600 hover:bg-emerald-700 text-white">
            <Check className="h-3.5 w-3.5" /> Approve & Continue
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Project Overview</label>
        <Textarea value={editOverview} onChange={e => setEditOverview(e.target.value)} rows={3} className="bg-background text-sm" />
      </div>

      <EditableList label="Functional Requirements" items={editFunc} setter={setEditFunc} />
      <EditableList label="Non-Functional Requirements" items={editNonFunc} setter={setEditNonFunc} />
      <EditableList label="User Roles" items={editRoles} setter={setEditRoles} />

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Technology Stack</label>
        <div className="grid grid-cols-2 gap-2 bg-background p-3 rounded-lg border">
          {(["frontend", "backend", "database", "ai_framework"] as const).map(k => (
            <div key={k}>
              <span className="text-[10px] text-muted-foreground uppercase font-medium">{k.replace("_", " ")}</span>
              <Input
                value={editStack[k]}
                onChange={e => setEditStack(p => ({ ...p, [k]: e.target.value }))}
                className="h-8 mt-1 text-sm"
              />
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">User Stories</label>
          <Button variant="ghost" size="sm" onClick={() => setEditStories(p => [...p, { role: "", desire: "", benefit: "" }])} className="h-6 gap-1 text-primary text-xs">
            <Plus className="h-3 w-3" /> Add
          </Button>
        </div>
        {editStories.map((story, i) => (
          <div key={i} className="flex flex-col gap-1 bg-background p-2.5 rounded-lg border">
            <div className="flex gap-1 items-center">
              <span className="text-xs text-muted-foreground w-14 shrink-0">As a</span>
              <Input value={story.role} onChange={e => setEditStories(p => p.map((s, j) => j === i ? { ...s, role: e.target.value } : s))} className="h-7 text-xs flex-1" />
              <Button variant="ghost" size="icon" onClick={() => setEditStories(p => p.filter((_, j) => j !== i))} className="h-7 w-7 text-destructive shrink-0">
                <Trash className="h-3 w-3" />
              </Button>
            </div>
            <div className="flex gap-1 items-center">
              <span className="text-xs text-muted-foreground w-14 shrink-0">I want to</span>
              <Input value={story.desire} onChange={e => setEditStories(p => p.map((s, j) => j === i ? { ...s, desire: e.target.value } : s))} className="h-7 text-xs flex-1" />
            </div>
            <div className="flex gap-1 items-center">
              <span className="text-xs text-muted-foreground w-14 shrink-0">So that</span>
              <Input value={story.benefit} onChange={e => setEditStories(p => p.map((s, j) => j === i ? { ...s, benefit: e.target.value } : s))} className="h-7 text-xs flex-1" />
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end pt-2 border-t">
        <Button size="sm" onClick={handleSave} className="gap-1 bg-emerald-600 hover:bg-emerald-700 text-white">
          <Check className="h-3.5 w-3.5" /> Approve & Continue to Architecture
        </Button>
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export function RequirementsPanel({
  initialIdea,
  requirements: initialRequirements,
  onRequirementsGenerated,
}: {
  initialIdea?: string | null;
  requirements?: RequirementsResponse | null;
  onRequirementsGenerated?: (data: RequirementsResponse) => void;
}) {
  // Mode: "choose" | "interview" | "quick" | "review" | "done"
  const [mode, setMode] = useState<"choose" | "interview" | "quick" | "review" | "done">(
    initialRequirements ? "done" : "choose"
  );

  // Interview state
  const [idea, setIdea] = useState(initialIdea || "");
  const [history, setHistory] = useState<ElicitationMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [currentPhase, setCurrentPhase] = useState(1);
  const [phaseLabel, setPhaseLabel] = useState("");
  const [phaseDesc, setPhaseDesc] = useState("");
  const [progressPct, setProgressPct] = useState(0);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result state
  const [result, setResult] = useState<RequirementsResponse | null>(initialRequirements ?? null);
  const [isEditing, setIsEditing] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const answerRef = useRef<HTMLTextAreaElement>(null);

  // Keep display history (without the pending question)
  const displayHistory = history.filter(m => m.role === "user");

  useEffect(() => {
    if (initialRequirements) {
      setResult(initialRequirements);
      setMode("done");
    }
  }, [initialRequirements]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, currentQuestion]);

  // Start the interview
  const handleStartInterview = async () => {
    if (!idea.trim()) { toast.error("Please describe your project idea first."); return; }
    setLoading(true);
    setError(null);
    setMode("interview");
    try {
      const res = await startElicitation(idea.trim());
      setHistory(res.history);
      setCurrentQuestion(res.question);
      setCurrentPhase(res.phase);
      setPhaseLabel(res.phase_label);
      setPhaseDesc(res.phase_description);
      setProgressPct(res.progress_pct);
      answerRef.current?.focus();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Failed to start interview.");
      setMode("choose");
    } finally {
      setLoading(false);
    }
  };

  // Send an answer
  const handleSendAnswer = async () => {
    if (!answer.trim()) { toast.error("Please provide an answer before continuing."); return; }
    const myAnswer = answer.trim();
    setAnswer("");
    setLoading(true);
    setError(null);

    // Optimistically append user message to display
    const userMsg: ElicitationMessage = { role: "user", content: myAnswer, phase: currentPhase };
    const updatedHistory = [...history, userMsg];
    setHistory(updatedHistory);

    try {
      const res = await sendElicitationAnswer(idea.trim(), myAnswer, history);
      setHistory(res.history);
      setCurrentPhase(res.phase);
      setPhaseLabel(res.phase_label);
      setPhaseDesc(res.phase_description);
      setProgressPct(res.progress_pct);

      if (res.is_complete && res.requirements) {
        setResult(res.requirements);
        setCurrentQuestion("");
        setMode("review");
        toast.success("Interview complete! Review your synthesised requirements below.", { duration: 5000 });
      } else {
        setCurrentQuestion(res.question);
        setTimeout(() => answerRef.current?.focus(), 100);
      }
    } catch (err: any) {
      // Rollback optimistic update
      setHistory(history);
      setAnswer(myAnswer);
      setError(err?.response?.data?.detail ?? err?.message ?? "Failed to send answer.");
    } finally {
      setLoading(false);
    }
  };

  // Quick generate (legacy)
  const handleQuickGenerate = async () => {
    if (!idea.trim()) { toast.error("Please describe your project idea first."); return; }
    setLoading(true);
    setError(null);
    setMode("quick");
    try {
      const data = await createRequirements(idea.trim());
      setResult(data);
      setMode("review");
      if (onRequirementsGenerated) onRequirementsGenerated(data);
      toast.success("Requirements generated! Review and edit below.");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Generation failed.");
      setMode("choose");
    } finally {
      setLoading(false);
    }
  };

  // Approve requirements
  const handleApprove = (updated: RequirementsResponse) => {
    setResult(updated);
    setIsEditing(false);
    setMode("done");
    if (onRequirementsGenerated) onRequirementsGenerated(updated);
    toast.success("Requirements approved and locked in! Proceed to Architecture →");
  };

  // Reset
  const handleReset = () => {
    setMode("choose");
    setHistory([]);
    setCurrentQuestion("");
    setAnswer("");
    setResult(null);
    setError(null);
    setProgressPct(0);
  };

  // Keyboard shortcut: Ctrl+Enter sends answer
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") handleSendAnswer();
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <Card className="shadow-card">
      <CardHeader className="pb-3 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <MessageSquare className="h-5 w-5 text-primary" />
              Requirements Elicitation
              {mode === "done" && <Badge variant="outline" className="text-emerald-600 border-emerald-500/40 bg-emerald-500/10 ml-1">Approved</Badge>}
              {mode === "interview" && <Badge variant="outline" className="text-primary border-primary/40 bg-primary/10 ml-1">Interview Active</Badge>}
            </CardTitle>
            <CardDescription>
              {mode === "choose" && "Guided interview following BABOK v3 methodology — no AI hallucination"}
              {mode === "interview" && `Phase ${currentPhase}/6 — ${phaseLabel}`}
              {(mode === "review" || mode === "quick") && "Synthesised from your answers — review and approve"}
              {mode === "done" && "Developer-validated requirements specification (IEEE Std 830)"}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {mode === "done" && (
              <>
                <Button variant="outline" size="sm" onClick={() => setIsEditing(true)} className="gap-1 text-primary">
                  <Edit3 className="h-3.5 w-3.5" /> Edit
                </Button>
                <Button variant="ghost" size="sm" onClick={handleReset} className="gap-1 text-muted-foreground">
                  <RotateCcw className="h-3.5 w-3.5" /> Re-elicit
                </Button>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {/* ── Error ─────────────────────────────────────────────────────── */}
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* ── MODE: CHOOSE ──────────────────────────────────────────────── */}
        {mode === "choose" && (
          <div className="space-y-4">
            {/* Idea input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Describe your project idea in a sentence or two:
              </label>
              <Textarea
                placeholder="e.g. A hospital inventory management system that tracks medical supplies across wards and alerts staff when stock is low..."
                value={idea}
                onChange={e => setIdea(e.target.value)}
                rows={3}
                className="resize-none bg-background"
              />
            </div>

            {/* Mode cards */}
            <div className="grid gap-3 sm:grid-cols-2">
              {/* Interview mode */}
              <button
                type="button"
                onClick={handleStartInterview}
                disabled={loading || !idea.trim()}
                className="group text-left rounded-xl border-2 border-primary/30 bg-primary/5 p-4 hover:border-primary/60 hover:bg-primary/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">Guided Interview</p>
                    <p className="text-[10px] text-primary font-medium uppercase tracking-wide">Recommended</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  AI interviews you like a real Business Analyst across 6 structured phases 
                  (BABOK v3). Requirements come from <em>your</em> answers — not AI guesswork.
                </p>
                <div className="flex flex-wrap gap-1 mt-3">
                  {PHASES.map(p => (
                    <span key={p.label} className="text-[9px] bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">
                      {p.icon} {p.label.split(" ")[0]}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-1 mt-3 text-xs text-primary font-medium">
                  Start Interview <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </button>

              {/* Quick mode */}
              <button
                type="button"
                onClick={handleQuickGenerate}
                disabled={loading || !idea.trim()}
                className="group text-left rounded-xl border border-border bg-muted/20 p-4 hover:border-border/80 hover:bg-muted/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted border border-border text-muted-foreground">
                    <Zap className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">Quick Generate</p>
                    <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide">Fast / Demo mode</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  AI generates requirements from your description in one shot. 
                  Faster, but may hallucinate details you didn't specify.
                </p>
                <div className="flex items-center gap-1 mt-7 text-xs text-muted-foreground font-medium">
                  Generate Now <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </button>
            </div>

            {loading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                <Loader2 className="h-4 w-4 animate-spin" />
                Starting elicitation session…
              </div>
            )}
          </div>
        )}

        {/* ── MODE: INTERVIEW ────────────────────────────────────────────── */}
        {mode === "interview" && (
          <div className="space-y-4">
            {/* Phase progress */}
            <PhaseProgress currentPhase={currentPhase} progress={progressPct} />

            {/* Chat transcript */}
            <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1 scroll-smooth">
              {/* Render completed turns */}
              {history.map((msg, i) => (
                <ChatBubble key={i} msg={msg} isLatest={i === history.length - 1} />
              ))}

              {/* Current question (not yet in history when waiting for answer) */}
              {currentQuestion && !loading && (
                <ChatBubble
                  msg={{ role: "assistant", content: currentQuestion, phase: currentPhase }}
                  isLatest={true}
                />
              )}

              {/* Loading indicator */}
              {loading && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground animate-pulse pl-10">
                  <div className="flex gap-1">
                    <div className="h-1.5 w-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="h-1.5 w-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="h-1.5 w-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                  Requirements Analyst is thinking…
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Answer input */}
            {!loading && currentQuestion && (
              <div className="space-y-2 border-t border-border pt-3">
                <div className="flex items-start gap-2">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted border border-border">
                    <User className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                  <Textarea
                    ref={answerRef}
                    placeholder="Type your answer… (Ctrl+Enter to send)"
                    value={answer}
                    onChange={e => setAnswer(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={3}
                    className="resize-none bg-background flex-1 text-sm"
                    disabled={loading}
                  />
                </div>
                <div className="flex items-center justify-between pl-9">
                  <p className="text-[10px] text-muted-foreground">
                    Phase {currentPhase}/6 · {phaseDesc}
                  </p>
                  <Button
                    size="sm"
                    onClick={handleSendAnswer}
                    disabled={loading || !answer.trim()}
                    className="gap-1.5"
                  >
                    <ChevronRight className="h-3.5 w-3.5" />
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── MODE: QUICK LOADING ────────────────────────────────────────── */}
        {mode === "quick" && loading && (
          <div className="space-y-2 mt-2 animate-pulse">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating requirements from your description…
            </div>
            {[...Array(5)].map((_, i) => <div key={i} className="h-10 rounded-lg bg-muted/60" />)}
          </div>
        )}

        {/* ── MODE: REVIEW (edit form) ───────────────────────────────────── */}
        {(mode === "review") && result && !loading && (
          <RequirementsEditForm
            result={result}
            onSave={handleApprove}
            onCancel={() => { setMode("choose"); setResult(null); }}
          />
        )}

        {/* ── MODE: DONE (display result) ────────────────────────────────── */}
        {mode === "done" && result && !isEditing && (
          <div className="space-y-3">
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <h2 className="font-semibold text-base text-foreground">{result.project_name}</h2>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{result.project_overview}</p>
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
              {(result.user_stories || []).map((s, i) => (
                <div key={i} className="rounded-md border border-border bg-muted/20 px-3 py-2 text-sm mb-2">
                  <p><span className="font-medium text-primary">As a</span> {s.role},</p>
                  <p><span className="font-medium">I want to</span> {s.desire}</p>
                  <p><span className="font-medium text-emerald-600">so that</span> {s.benefit}.</p>
                </div>
              ))}
            </AccordionSection>
            <AccordionSection title="Suggested Modules" badge={result.suggested_modules?.length}>
              <BulletList items={result.suggested_modules || []} />
            </AccordionSection>
            <AccordionSection title="Assumptions & Constraints">
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Assumptions</p>
                <BulletList items={result.assumptions || []} />
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mt-3">Constraints</p>
                <BulletList items={result.constraints || []} />
              </div>
            </AccordionSection>
            <AccordionSection title="Recommended Tech Stack">
              <TechStackGrid stack={result.recommended_tech_stack} />
            </AccordionSection>
          </div>
        )}

        {/* Edit overlay */}
        {mode === "done" && result && isEditing && (
          <RequirementsEditForm
            result={result}
            onSave={handleApprove}
            onCancel={() => setIsEditing(false)}
          />
        )}
      </CardContent>
    </Card>
  );
}
