import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "sonner";
import {
  LogOut, Plus, FileText, Download, Trash2, ArrowLeft, Loader2,
  BarChart3, Clock, CheckCircle2, AlertCircle, Layers, FolderOpen,
  Zap, TrendingUp, Code2, BookOpen, Database as DbIcon, Cpu, ChevronRight
} from "lucide-react";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { ProjectForm } from "@/components/dashboard/ProjectForm";
import { AgentProgress } from "@/components/dashboard/AgentProgress";
import { ResultsTabs } from "@/components/dashboard/ResultsTabs";
import { GeneratedFiles } from "@/components/dashboard/GeneratedFiles";
import { initialAgents, type Agent } from "@/lib/blueprint-data";
import { useAuth } from "@/lib/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { supabase } from "@/lib/supabase";
import {
  fetchProjects, fetchFullProject, createProject, updateProjectStatus,
  saveRequirements, saveArchitecture, saveDatabase, saveDocumentation,
  saveScaffoldFiles, logGenerationEvent, deleteProject,
  type ProjectSummary, type FullProject
} from "@/services/projects";
import { exportBlueprintPdf } from "@/services/export";
import { exportBlueprintDocx } from "@/services/export_docx";
import { downloadScaffoldZip } from "@/services/scaffold";
import { createRequirements, type RequirementsResponse } from "@/services/requirements";
import { generateArchitecture, type ArchitectureResponse } from "@/services/architecture";
import { generateDatabase, type DatabaseResponse, type ProjectContextInput } from "@/services/database";
import { generateDocumentation, type DocumentationResponse } from "@/services/documentation";
import { generateScaffold, type ScaffoldResponse } from "@/services/scaffold";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Blueprint" },
      { name: "description", content: "Manage your AI-generated project blueprints." },
    ],
  }),
  beforeLoad: async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) throw redirect({ to: "/login" });
  },
  component: Dashboard,
});

// ─── Agent step metadata ──────────────────────────────────────────────────────
const PIPELINE_STEPS = [
  { id: "requirements", label: "Requirements Analyst", icon: BookOpen, color: "text-violet-500", desc: "Extracting objectives, user stories & tech stack" },
  { id: "architect",   label: "Software Architect",   icon: Layers,   color: "text-indigo-500", desc: "Designing components, patterns & folder structure" },
  { id: "database",    label: "Database Designer",    icon: DbIcon,   color: "text-blue-500",   desc: "Generating schema, entities & ER diagram" },
  { id: "docs",        label: "Documentation Agent",  icon: FileText, color: "text-cyan-500",   desc: "Writing README, API docs & installation guides" },
  { id: "scaffold",    label: "Project Scaffold",     icon: Code2,    color: "text-emerald-500",desc: "Creating all project files & directory tree" },
] as const;

type PipelineStepId = typeof PIPELINE_STEPS[number]["id"];

// ─── Dashboard component ──────────────────────────────────────────────────────
function Dashboard() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  // View state
  const [activeView, setActiveView] = useState<"list" | "create">("list");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  // Current project being worked on (when in create view)
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [currentRequirements, setCurrentRequirements] = useState<RequirementsResponse | null>(null);
  const [currentArchitecture, setCurrentArchitecture] = useState<ArchitectureResponse | null>(null);
  const [currentDatabase, setCurrentDatabase] = useState<DatabaseResponse | null>(null);
  const [currentDocumentation, setCurrentDocumentation] = useState<DocumentationResponse | null>(null);
  const [currentScaffold, setCurrentScaffold] = useState<ScaffoldResponse | null>(null);

  // Pipeline state
  const [generating, setGenerating] = useState(false);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<PipelineStepId | null>(null);
  const [stepProgress, setStepProgress] = useState<Record<string, number>>({});
  const [agents, setAgents] = useState<Agent[]>(
    initialAgents.map(a => ({ ...a, status: "waiting" as const, progress: 0 }))
  );

  // ─── Project list loading ────────────────────────────────────────────────────
  const loadProjects = useCallback(async () => {
    if (!user) return;
    setLoadingProjects(true);
    try {
      const data = await fetchProjects(user.id);
      setProjects(data);
    } catch {
      toast.error("Could not load your saved blueprints.");
    } finally {
      setLoadingProjects(false);
    }
  }, [user]);

  useEffect(() => { if (user) loadProjects(); }, [user, loadProjects]);

  // ─── Agent sidebar sync ──────────────────────────────────────────────────────
  const updateAgentState = (
    stepId: string,
    status: Agent["status"],
    progress: number
  ) => {
    setAgents(prev =>
      prev.map(a =>
        a.id === stepId ? { ...a, status, progress } : a
      )
    );
  };

  // ─── Full pipeline runner (automated) ────────────────────────────────────────
  const runPipeline = useCallback(async (name: string, desc: string, techStack: string) => {
    if (!user) return;

    setGenerating(true);
    setPipelineError(null);

    // Reset all state
    setCurrentRequirements(null);
    setCurrentArchitecture(null);
    setCurrentDatabase(null);
    setCurrentDocumentation(null);
    setCurrentScaffold(null);
    setAgents(initialAgents.map(a => ({ ...a, status: "waiting" as const, progress: 0 })));

    let projectId: string;
    try {
      projectId = await createProject(user.id, name, desc, techStack);
      setCurrentProjectId(projectId);
      await updateProjectStatus(projectId, "generating");
    } catch (err) {
      toast.error("Failed to create project record in database.");
      setGenerating(false);
      return;
    }

    const idea = `${name}: ${desc} (Tech Stack: ${techStack})`;
    let requirements: RequirementsResponse | null = null;
    let architecture: ArchitectureResponse | null = null;
    let database: DatabaseResponse | null = null;
    let documentation: DocumentationResponse | null = null;

    const runStep = async <T>(
      stepId: PipelineStepId,
      agentIdx: number,
      fn: () => Promise<T>
    ): Promise<T> => {
      const start = Date.now();
      setCurrentStep(stepId);
      updateAgentState(stepId, "running", 10);
      await logGenerationEvent(projectId, stepId, "started");

      // Animate progress while waiting
      let prog = 10;
      const interval = setInterval(() => {
        prog = Math.min(prog + 5, 88);
        updateAgentState(stepId, "running", prog);
      }, 800);

      try {
        const result = await fn();
        clearInterval(interval);
        updateAgentState(stepId, "completed", 100);
        await logGenerationEvent(projectId, stepId, "completed", Date.now() - start);
        await updateProjectStatus(projectId, "generating", agentIdx + 1);
        return result;
      } catch (err: any) {
        clearInterval(interval);
        updateAgentState(stepId, "waiting", 0);
        const msg = err?.response?.data?.detail ?? err?.message ?? "Unknown error";
        await logGenerationEvent(projectId, stepId, "failed", Date.now() - start, msg);
        throw new Error(`${stepId} failed: ${msg}`);
      }
    };

    try {
      // ── Step 1: Requirements ────────────────────────────────────────
      requirements = await runStep("requirements", 0, async () => {
        const r = await createRequirements(idea);
        setCurrentRequirements(r);
        await saveRequirements(projectId, r);
        return r;
      });

      // ── Step 2: Architecture ────────────────────────────────────────
      architecture = await runStep("architect", 1, async () => {
        const a = await generateArchitecture(requirements!);
        setCurrentArchitecture(a);
        await saveArchitecture(projectId, a);
        return a;
      });

      // ── Step 3: Database ────────────────────────────────────────────
      database = await runStep("database", 2, async () => {
        const ctx: ProjectContextInput = { requirements, architecture };
        const d = await generateDatabase(ctx);
        setCurrentDatabase(d);
        await saveDatabase(projectId, d);
        return d;
      });

      // ── Step 4: Documentation ───────────────────────────────────────
      documentation = await runStep("docs", 3, async () => {
        const ctx: ProjectContextInput = { requirements, architecture, database };
        const doc = await generateDocumentation(ctx);
        setCurrentDocumentation(doc);
        await saveDocumentation(projectId, doc);
        return doc;
      });

      // ── Step 5: Scaffold ────────────────────────────────────────────
      await runStep("scaffold", 4, async () => {
        const ctx: ProjectContextInput = { requirements, architecture, database, documentation };
        const scaffold = await generateScaffold(ctx);
        setCurrentScaffold(scaffold);
        await saveScaffoldFiles(projectId, scaffold);
        return scaffold;
      });

      // ── Mark project completed ──────────────────────────────────────
      const fileCount = currentScaffold?.total_files ?? 0;
      await updateProjectStatus(projectId, "completed", 5, fileCount);
      setCurrentStep(null);
      toast.success(`🎉 Blueprint generated! All 5 agents completed.`);
      loadProjects();

    } catch (err: any) {
      setPipelineError(err.message ?? "Pipeline failed.");
      await updateProjectStatus(projectId, "failed");
      toast.error(err.message ?? "Generation pipeline failed.");
    } finally {
      setGenerating(false);
    }
  }, [user, loadProjects, currentScaffold]);

  // ─── View project (load from DB) ────────────────────────────────────────────
  const handleViewProject = async (p: ProjectSummary) => {
    try {
      const full = await fetchFullProject(p.id);
      if (!full) { toast.error("Could not load project details."); return; }
      setCurrentProjectId(p.id);
      setCurrentRequirements(full.requirements);
      setCurrentArchitecture(full.architecture);
      setCurrentDatabase(full.database_design);
      setCurrentDocumentation(full.documentation);
      setCurrentScaffold(full.scaffold);
      // Reflect completed state in the sidebar
      setAgents(initialAgents.map((a, i) => {
        const done = i < (full.agents_done ?? 0);
        return { ...a, status: done ? "completed" : "waiting", progress: done ? 100 : 0 };
      }));
      setActiveView("create");
    } catch {
      toast.error("Failed to load project.");
    }
  };

  // ─── Delete project ──────────────────────────────────────────────────────────
  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this blueprint? This cannot be undone.")) return;
    try {
      await deleteProject(id);
      toast.success("Blueprint deleted.");
      loadProjects();
    } catch { toast.error("Failed to delete."); }
  };

  // ─── Create new ──────────────────────────────────────────────────────────────
  const handleCreateNew = () => {
    setCurrentProjectId(null);
    setCurrentRequirements(null);
    setCurrentArchitecture(null);
    setCurrentDatabase(null);
    setCurrentDocumentation(null);
    setCurrentScaffold(null);
    setPipelineError(null);
    setCurrentStep(null);
    setAgents(initialAgents.map(a => ({ ...a, status: "waiting" as const, progress: 0 })));
    setActiveView("create");
  };

  // ─── Download helpers ────────────────────────────────────────────────────────
  const downloadZip = async (p: ProjectSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    if (p.total_files === 0) { toast.error("No scaffold files available."); return; }
    const full = await fetchFullProject(p.id);
    if (!full?.scaffold) { toast.error("No scaffold data found."); return; }
    try { await downloadScaffoldZip(full.scaffold); }
    catch { toast.error("ZIP download failed."); }
  };

  const downloadPdf = async (p: ProjectSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    const full = await fetchFullProject(p.id);
    if (!full) return;
    const ctx: ProjectContextInput = { requirements: full.requirements, architecture: full.architecture, database: full.database_design, documentation: full.documentation };
    const blob = await exportBlueprintPdf(ctx);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${p.name.toLowerCase().replace(/\s+/g, "_")}_blueprint.pdf`;
    a.click();
  };

  const downloadDocx = async (p: ProjectSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    const full = await fetchFullProject(p.id);
    if (!full) return;
    const ctx: ProjectContextInput = { requirements: full.requirements, architecture: full.architecture, database: full.database_design, documentation: full.documentation };
    const blob = await exportBlueprintDocx(ctx);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${p.name.toLowerCase().replace(/\s+/g, "_")}_blueprint.docx`;
    a.click();
  };

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out.");
    navigate({ to: "/" });
  };

  // ─── Computed stats ──────────────────────────────────────────────────────────
  const totalProjects = projects.length;
  const completedProjects = projects.filter(p => p.status === "completed").length;
  const totalFiles = projects.reduce((s, p) => s + (p.total_files ?? 0), 0);
  const thisWeek = projects.filter(p => {
    const d = new Date(p.created_at);
    const now = new Date();
    const diff = (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24);
    return diff <= 7;
  }).length;

  const savedContext: ProjectContextInput = {
    requirements: currentRequirements,
    architecture: currentArchitecture,
    database: currentDatabase,
    documentation: currentDocumentation,
  };

  // Derived agent pipeline status to keep sidebar reactive
  const derivedAgents = PIPELINE_STEPS.map((step) => {
    if (generating) {
      const activeAgent = agents.find((a) => a.id === step.id);
      return {
        id: step.id,
        name: step.label,
        description: step.desc,
        status: activeAgent?.status ?? "waiting",
        progress: activeAgent?.progress ?? 0,
      };
    }
    
    let status: Agent["status"] = "waiting";
    let progress = 0;

    if (step.id === "requirements" && currentRequirements) {
      status = "completed";
      progress = 100;
    } else if (step.id === "architect" && currentArchitecture) {
      status = "completed";
      progress = 100;
    } else if (step.id === "database" && currentDatabase) {
      status = "completed";
      progress = 100;
    } else if (step.id === "docs" && currentDocumentation) {
      status = "completed";
      progress = 100;
    } else if (step.id === "scaffold" && currentScaffold) {
      status = "completed";
      progress = 100;
    }

    return {
      id: step.id,
      name: step.label,
      description: step.desc,
      status,
      progress,
    };
  });

  // Completion percentage
  const completedSteps = derivedAgents.filter(a => a.status === "completed").length;
  const overallProgress = generating ? Math.round((completedSteps / 5) * 100) : (currentProjectId ? Math.round((completedSteps / 5) * 100) : 0);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            {activeView === "create" && (
              <Button variant="ghost" size="icon" onClick={() => { setActiveView("list"); loadProjects(); }}
                className="shrink-0 rounded-xl border border-border">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {activeView === "list" ? "My Blueprints" : "Blueprint Workspace"}
              </h1>
              <p className="text-sm text-muted-foreground">
                {activeView === "list"
                  ? `Hello, ${user?.user_metadata?.full_name ?? user?.email} 👋`
                  : currentProjectId
                    ? generating ? `Running pipeline — ${completedSteps}/5 agents done`
                      : "View or re-generate your blueprint"
                    : "Describe your project to generate a full blueprint"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {activeView === "list" && (
              <Button onClick={handleCreateNew}
                className="gap-2 bg-brand text-brand-foreground shadow hover:bg-brand/90">
                <Plus className="h-4 w-4" /> New Blueprint
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={handleSignOut}
              className="gap-1.5 text-muted-foreground hover:text-foreground">
              <LogOut className="h-4 w-4" /> Sign out
            </Button>
          </div>
        </div>

        {/* ════════════════════════════════════════════════════════════════
            VIEW 1 — LIST (DASHBOARD)
         ═══════════════════════════════════════════════════════════════ */}
        {activeView === "list" && (
          <div className="space-y-8">

            {/* ── Stats Row ─────────────────────────────────────────────── */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Total Blueprints", value: totalProjects, icon: Layers, color: "text-violet-500", bg: "bg-violet-500/10", sub: `${completedProjects} completed` },
                { label: "Total Files Generated", value: totalFiles, icon: Code2, color: "text-indigo-500", bg: "bg-indigo-500/10", sub: "across all projects" },
                { label: "This Week", value: thisWeek, icon: TrendingUp, color: "text-emerald-500", bg: "bg-emerald-500/10", sub: "new blueprints" },
                { label: "AI Engine", value: "Qwen 3", icon: Cpu, color: "text-amber-500", bg: "bg-amber-500/10", sub: "8B model · Local Ollama" },
              ].map((s) => (
                <Card key={s.label} className="border-border/60 shadow-card hover:shadow-elevated transition-shadow">
                  <CardContent className="flex items-start gap-4 pt-6">
                    <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${s.bg}`}>
                      <s.icon className={`h-5 w-5 ${s.color}`} />
                    </span>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{s.label}</p>
                      <p className="mt-0.5 text-2xl font-bold">{s.value}</p>
                      <p className="text-xs text-muted-foreground">{s.sub}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* ── Project Grid ──────────────────────────────────────────── */}
            {loadingProjects ? (
              <div className="flex flex-col items-center py-20 text-muted-foreground gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-brand" />
                <p className="text-sm">Loading your blueprints…</p>
              </div>
            ) : projects.length === 0 ? (
              <Card className="border-dashed border-2 border-border shadow-none bg-transparent py-16">
                <div className="mx-auto max-w-md space-y-4 text-center">
                  <div className="mx-auto h-16 w-16 rounded-2xl bg-brand/10 flex items-center justify-center">
                    <Zap className="h-8 w-8 text-brand" />
                  </div>
                  <h3 className="text-xl font-semibold">No blueprints yet</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Describe any software project and our 5-agent AI pipeline will generate requirements, architecture, database schema, documentation, and a full code scaffold automatically.
                  </p>
                  <Button onClick={handleCreateNew} className="gap-2 bg-brand text-brand-foreground">
                    <Plus className="h-4 w-4" /> Create your first blueprint
                  </Button>
                </div>
              </Card>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold text-foreground">All Blueprints</h2>
                  <span className="text-xs text-muted-foreground">{projects.length} project{projects.length !== 1 ? "s" : ""}</span>
                </div>
                <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                  {projects.map((p) => {
                    const statusIcon =
                      p.status === "completed" ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> :
                      p.status === "generating" ? <Loader2 className="h-3.5 w-3.5 animate-spin text-brand" /> :
                      p.status === "failed" ? <AlertCircle className="h-3.5 w-3.5 text-destructive" /> :
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />;

                    const progress = Math.round(((p.agents_done ?? 0) / (p.total_agents ?? 5)) * 100);

                    return (
                      <Card
                        key={p.id}
                        className="group flex flex-col border-border/60 shadow-card hover:shadow-elevated hover:border-brand/40 transition-all duration-200 cursor-pointer"
                        onClick={() => handleViewProject(p)}
                      >
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between gap-2">
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2">
                                {statusIcon}
                                <CardTitle className="text-sm font-semibold truncate group-hover:text-brand transition-colors">
                                  {p.name}
                                </CardTitle>
                              </div>
                              {p.tech_stack && (
                                <span className="mt-1 inline-block rounded-full bg-brand/10 px-2 py-0.5 text-[10px] font-semibold text-brand">
                                  {p.tech_stack}
                                </span>
                              )}
                            </div>
                            <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 group-hover:text-brand group-hover:translate-x-0.5 transition-all" />
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2 mt-2">
                            {p.description || "No description."}
                          </p>
                        </CardHeader>

                        <CardContent className="pt-0 space-y-3">
                          {/* Pipeline progress bar */}
                          <div className="space-y-1">
                            <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                              <span>{p.agents_done ?? 0}/5 agents</span>
                              <span>{progress}%</span>
                            </div>
                            <Progress value={progress} className="h-1.5" />
                          </div>

                          {/* Stats row */}
                          <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border/50 pt-3">
                            <div className="flex items-center gap-1">
                              <FolderOpen className="h-3 w-3" />
                              <span>{p.total_files} files</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              <span>{new Date(p.created_at).toLocaleDateString("en-US", { month:"short", day:"numeric" })}</span>
                            </div>
                          </div>

                          {/* Action buttons */}
                          <div className="flex items-center justify-between border-t border-border/50 pt-3">
                            <div className="flex items-center gap-1">
                              <Button title="Download ZIP" variant="ghost" size="icon"
                                className="h-7 w-7 rounded-lg text-muted-foreground hover:text-brand"
                                onClick={(e) => downloadZip(p, e)} disabled={!p.total_files}>
                                <Download className="h-3.5 w-3.5" />
                              </Button>
                              <Button title="Download PDF" variant="ghost" size="icon"
                                className="h-7 w-7 rounded-lg text-muted-foreground hover:text-red-500"
                                onClick={(e) => downloadPdf(p, e)}>
                                <FileText className="h-3.5 w-3.5" />
                              </Button>
                              <Button title="Download DOCX" variant="ghost" size="icon"
                                className="h-7 w-7 rounded-lg text-muted-foreground hover:text-blue-500"
                                onClick={(e) => downloadDocx(p, e)}>
                                <BookOpen className="h-3.5 w-3.5" />
                              </Button>
                            </div>
                            <Button title="Delete" variant="ghost" size="icon"
                              className="h-7 w-7 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                              onClick={(e) => handleDelete(p.id, e)}>
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            VIEW 2 — CREATION WORKSPACE
         ═══════════════════════════════════════════════════════════════ */}
        {activeView === "create" && (
          <div className="grid gap-6 lg:grid-cols-12">

            {/* ── Left column — Form + Progress ─────────────────────────── */}
            <div className="space-y-5 lg:col-span-4">

              {/* Only show form when not generating and no project loaded */}
              {!generating && !currentProjectId && (
                <ProjectForm onGenerate={runPipeline} generating={generating} />
              )}

              {/* Re-generate button if viewing existing project */}
              {!generating && currentProjectId && (
                <Card className="border-dashed border-2 border-border/60 shadow-none">
                  <CardContent className="py-5 text-center space-y-3">
                    <p className="text-sm font-medium">Blueprint loaded from database</p>
                    <p className="text-xs text-muted-foreground">
                      You can browse all generated sections or create a new blueprint from scratch.
                    </p>
                    <Button onClick={handleCreateNew} size="sm" className="w-full gap-2 bg-brand text-brand-foreground">
                      <Plus className="h-4 w-4" /> New Blueprint
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Pipeline progress — always visible when in create view */}
              <Card className="shadow-card">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base">Agent Pipeline</CardTitle>
                      <CardDescription className="text-xs">
                        {generating ? `Step ${completedSteps + 1} of 5 running…` : 
                         completedSteps === 5 ? "All agents completed ✓" : "Waiting to start"}
                      </CardDescription>
                    </div>
                    {generating && (
                      <span className="text-xs font-semibold text-brand">
                        {overallProgress}%
                      </span>
                    )}
                  </div>
                  {(generating || completedSteps > 0) && (
                    <Progress value={overallProgress} className="h-1.5 mt-2" />
                  )}
                </CardHeader>
                <CardContent className="pt-0">
                  <ol className="space-y-3">
                    {PIPELINE_STEPS.map((step, i) => {
                      const agent = derivedAgents.find(a => a.id === step.id);
                      const status = agent?.status ?? "waiting";
                      const progress = agent?.progress ?? 0;
                      const StepIcon = step.icon;

                      return (
                        <li key={step.id} className="flex items-start gap-3">
                          {/* Step circle */}
                          <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition-all ${
                            status === "completed" ? "border-emerald-500 bg-emerald-500" :
                            status === "running"   ? "border-brand bg-brand" :
                            "border-border bg-muted"
                          }`}>
                            {status === "completed" ? (
                              <CheckCircle2 className="h-4 w-4 text-white" />
                            ) : status === "running" ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin text-white" />
                            ) : (
                              <span className="text-xs font-bold text-muted-foreground">{i + 1}</span>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                              <p className={`text-sm font-medium ${status === "completed" ? "text-emerald-600" : status === "running" ? "text-brand" : "text-muted-foreground"}`}>
                                {step.label}
                              </p>
                              {status === "running" && (
                                <span className="text-xs text-muted-foreground shrink-0">{progress}%</span>
                              )}
                              {status === "completed" && (
                                <span className="text-[10px] font-semibold text-emerald-600 shrink-0">Done</span>
                              )}
                            </div>
                            <p className="text-[11px] text-muted-foreground leading-tight mt-0.5">
                              {status === "running" ? step.desc : 
                               status === "completed" ? "Completed successfully" : "Waiting…"}
                            </p>
                            {status === "running" && (
                              <div className="mt-1.5 h-1 w-full rounded-full bg-muted overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-brand transition-all duration-500"
                                  style={{ width: `${progress}%` }}
                                />
                              </div>
                            )}
                          </div>
                        </li>
                      );
                    })}
                  </ol>

                  {pipelineError && (
                    <div className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-xs text-destructive">
                      <AlertCircle className="inline h-3.5 w-3.5 mr-1.5" />
                      {pipelineError}
                    </div>
                  )}
                </CardContent>
              </Card>

              {generating && (
                <Card className="border-brand/30 bg-brand/5 shadow-none">
                  <CardContent className="py-4 text-center text-xs text-brand font-medium">
                    <Loader2 className="inline h-3.5 w-3.5 animate-spin mr-1.5" />
                    Running AI agents… this may take a few minutes.
                  </CardContent>
                </Card>
              )}
            </div>

            {/* ── Right column — Results ─────────────────────────────────── */}
            <div className="space-y-5 lg:col-span-8">
              <ResultsTabs
                initialIdea={null}
                savedContext={savedContext}
                savedScaffold={currentScaffold}
                onRequirementsUpdate={setCurrentRequirements}
                onArchitectureUpdate={setCurrentArchitecture}
                onDatabaseUpdate={setCurrentDatabase}
                onDocumentationUpdate={setCurrentDocumentation}
                onScaffoldGenerated={setCurrentScaffold}
              />
              <GeneratedFiles scaffold={currentScaffold} />
            </div>

          </div>
        )}

      </main>
      <Footer />
    </div>
  );
}
