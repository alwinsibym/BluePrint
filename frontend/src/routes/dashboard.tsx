import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { LogOut, Plus, FileText, Download, Trash2, ArrowLeft, Loader2, Database, LayoutGrid, BarChart3, Clock } from "lucide-react";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { ProjectForm } from "@/components/dashboard/ProjectForm";
import { AgentProgress } from "@/components/dashboard/AgentProgress";
import { ResultsTabs } from "@/components/dashboard/ResultsTabs";
import { GeneratedFiles } from "@/components/dashboard/GeneratedFiles";
import { initialAgents, type Agent } from "@/lib/blueprint-data";
import { generateBlueprint } from "@/services/api";
import { testLLM } from "@/services/llm";
import { ScaffoldResponse, downloadScaffoldZip } from "@/services/scaffold";
import { useAuth } from "@/lib/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { supabase } from "@/lib/supabase";
import { fetchProjects, saveProject, deleteProject, ProjectRecord } from "@/services/projects";
import { ProjectContextInput } from "@/services/database";
import { exportBlueprintPdf } from "@/services/export";
import { exportBlueprintDocx } from "@/services/export_docx";
import { RequirementsResponse } from "@/services/requirements";
import { ArchitectureResponse } from "@/services/architecture";
import { DatabaseResponse } from "@/services/database";
import { DocumentationResponse } from "@/services/documentation";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Blueprint" },
      { name: "description", content: "Generate and manage your project blueprints with multi-agent planning." },
    ],
  }),
  beforeLoad: async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      throw redirect({ to: "/login" });
    }
  },
  component: Dashboard,
});

function Dashboard() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  // State
  const [activeView, setActiveView] = useState<"list" | "create">("list");
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  // Generation state
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [generating, setGenerating] = useState(false);
  const [scaffold, setScaffold] = useState<ScaffoldResponse | null>(null);
  const [submittedIdea, setSubmittedIdea] = useState<string | null>(null);

  // The active project context we are viewing or generating
  const [currentRequirements, setCurrentRequirements] = useState<RequirementsResponse | null>(null);
  const [currentArchitecture, setCurrentArchitecture] = useState<ArchitectureResponse | null>(null);
  const [currentDatabase, setCurrentDatabase] = useState<DatabaseResponse | null>(null);
  const [currentDocumentation, setCurrentDocumentation] = useState<DocumentationResponse | null>(null);

  // If viewing a saved project, track its id
  const [viewedProjectId, setViewedProjectId] = useState<string | null>(null);

  // Load user's past projects from Supabase
  const loadProjects = async () => {
    if (!user) return;
    setLoadingProjects(true);
    try {
      const data = await fetchProjects(user.id);
      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
      toast.error("Could not load your saved blueprints.");
    } finally {
      setLoadingProjects(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadProjects();
    }
  }, [user]);

  // Synchronize sidebar progress dynamically with active generation/tab state
  useEffect(() => {
    setAgents((prev) =>
      prev.map((agent) => {
        if (agent.id === "requirements") {
          return currentRequirements
            ? { ...agent, status: "completed", progress: 100 }
            : generating
            ? { ...agent, status: "running", progress: 60 }
            : { ...agent, status: "waiting", progress: 0 };
        }
        if (agent.id === "architect") {
          return currentArchitecture
            ? { ...agent, status: "completed", progress: 100 }
            : currentRequirements && generating
            ? { ...agent, status: "running", progress: 50 }
            : { ...agent, status: "waiting", progress: 0 };
        }
        if (agent.id === "database") {
          return currentDatabase
            ? { ...agent, status: "completed", progress: 100 }
            : currentArchitecture && generating
            ? { ...agent, status: "running", progress: 40 }
            : { ...agent, status: "waiting", progress: 0 };
        }
        if (agent.id === "docs") {
          return currentDocumentation
            ? { ...agent, status: "completed", progress: 100 }
            : currentDatabase && generating
            ? { ...agent, status: "running", progress: 30 }
            : { ...agent, status: "waiting", progress: 0 };
        }
        if (agent.id === "scaffold") {
          return scaffold
            ? { ...agent, status: "completed", progress: 100 }
            : currentDocumentation && generating
            ? { ...agent, status: "running", progress: 20 }
            : { ...agent, status: "waiting", progress: 0 };
        }
        return agent;
      })
    );
  }, [currentRequirements, currentArchitecture, currentDatabase, currentDocumentation, scaffold, generating]);

  // When scaffolding is finished, automatically save the whole project to Supabase
  const handleScaffoldGenerated = async (scaffoldData: ScaffoldResponse) => {
    setScaffold(scaffoldData);
    if (!user) return;

    try {
      const context: ProjectContextInput = {
        requirements: currentRequirements,
        architecture: currentArchitecture,
        database: currentDatabase,
        documentation: currentDocumentation,
      };
      
      const projectName = currentRequirements?.project_name ?? "My AI Blueprint";
      const projectDesc = currentRequirements?.project_overview ?? "";
      const techStack = currentRequirements?.recommended_tech_stack
        ? `${currentRequirements.recommended_tech_stack.frontend} / ${currentRequirements.recommended_tech_stack.backend}`
        : "Standard Stack";

      await saveProject(
        user.id,
        projectName,
        projectDesc,
        techStack,
        context,
        scaffoldData,
        viewedProjectId
      );
      
      toast.success("Blueprint automatically saved to your dashboard!");
      loadProjects();
    } catch (err) {
      console.error("Auto-save failed:", err);
      toast.error("Completed generating, but failed to save to database.");
    }
  };

  const handleCreateNew = () => {
    setViewedProjectId(null);
    setCurrentRequirements(null);
    setCurrentArchitecture(null);
    setCurrentDatabase(null);
    setCurrentDocumentation(null);
    setScaffold(null);
    setSubmittedIdea(null);
    setAgents(initialAgents.map(a => ({ ...a, status: "waiting", progress: 0 })));
    setActiveView("create");
  };

  const handleViewProject = (p: ProjectRecord) => {
    setViewedProjectId(p.id);
    setCurrentRequirements(p.requirements);
    setCurrentArchitecture(p.architecture);
    setCurrentDatabase(p.database_design);
    setCurrentDocumentation(p.documentation);
    setScaffold(p.scaffold);
    setSubmittedIdea(p.requirements?.project_overview || "");
    setActiveView("create");
  };

  const handleDeleteProject = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this blueprint?")) return;
    try {
      await deleteProject(id);
      toast.success("Blueprint deleted.");
      loadProjects();
    } catch (err) {
      toast.error("Failed to delete project.");
    }
  };

  const onGenerate = async (name: string, description: string, techStack: string) => {
    setGenerating(true);
    setSubmittedIdea(`${name}: ${description} (Tech Stack: ${techStack})`);
    setCurrentRequirements(null);
    setCurrentArchitecture(null);
    setCurrentDatabase(null);
    setCurrentDocumentation(null);
    setScaffold(null);
    
    // Trigger agent workflows
    try {
      // Backend triggers are handled page-by-page by the user clicking next tabs or generating.
      // We set the initial state so our synchronizer triggers loader icons:
      setAgents(initialAgents.map(a => ({ ...a, status: a.id === "requirements" ? "running" : "waiting", progress: a.id === "requirements" ? 40 : 0 })));
      toast.info("Generating Requirements Analysts workflow...");
    } catch (error) {
      console.error(error);
      setGenerating(false);
    }
  };

  const handleDownloadZipForProject = async (p: ProjectRecord, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!p.scaffold) {
      toast.error("No scaffold files found to download.");
      return;
    }
    try {
      await downloadScaffoldZip(p.scaffold);
      toast.success("ZIP download started!");
    } catch (err) {
      toast.error("Failed to download ZIP.");
    }
  };

  const handleDownloadPdfForProject = async (p: ProjectRecord, e: React.MouseEvent) => {
    e.stopPropagation();
    const context: ProjectContextInput = {
      requirements: p.requirements,
      architecture: p.architecture,
      database: p.database_design,
      documentation: p.documentation,
    };
    try {
      const blob = await exportBlueprintPdf(context);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${p.name.toLowerCase().replace(/\s+/g, "_")}_blueprint.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error("Failed to export PDF.");
    }
  };

  const handleDownloadDocxForProject = async (p: ProjectRecord, e: React.MouseEvent) => {
    e.stopPropagation();
    const context: ProjectContextInput = {
      requirements: p.requirements,
      architecture: p.architecture,
      database: p.database_design,
      documentation: p.documentation,
    };
    try {
      const blob = await exportBlueprintDocx(context);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${p.name.toLowerCase().replace(/\s+/g, "_")}_blueprint.docx`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error("Failed to export Word Document.");
    }
  };

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out successfully.");
    navigate({ to: "/" });
  };

  const handleTestLLM = async () => {
    try {
      const res = await testLLM("Hello");
      toast.success(`LLM response: ${res.data.response}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      toast.error(`LLM error: ${msg}`);
    }
  };

  const savedContextInput: ProjectContextInput = {
    requirements: currentRequirements,
    architecture: currentArchitecture,
    database: currentDatabase,
    documentation: currentDocumentation,
  };

  return (
    <div className="flex min-h-screen flex-col bg-muted/20">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        
        {/* HEADER SECTION */}
        <div className="mb-8 flex flex-col justify-between gap-4 border-b border-border/60 pb-6 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
              {activeView === "list" ? "My Blueprints" : "Blueprint Workspace"}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {activeView === "list"
                ? `Welcome back, ${user?.user_metadata?.full_name || user?.email} — manage your planning credentials.`
                : "Create, review, and scaffold an AI-generated software project."}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {activeView === "list" ? (
              <Button onClick={handleCreateNew} className="gap-2 bg-brand text-brand-foreground shadow-md hover:bg-brand/90">
                <Plus className="h-4 w-4" /> Create New Blueprint
              </Button>
            ) : (
              <Button variant="outline" onClick={() => { setActiveView("list"); loadProjects(); }} className="gap-2">
                <ArrowLeft className="h-4 w-4" /> Back to Dashboard
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={handleSignOut} className="gap-2 text-muted-foreground hover:text-foreground">
              <LogOut className="h-4 w-4" /> Sign out
            </Button>
          </div>
        </div>

        {/* VIEW 1: PROJECT LIST VIEW (USER DASHBOARD) */}
        {activeView === "list" && (
          <div className="space-y-8">
            
            {/* Stats Cards */}
            <div className="grid gap-4 sm:grid-cols-3">
              <Card className="shadow-card border-border/60 bg-gradient-to-br from-card to-muted/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-xs uppercase font-semibold tracking-wider text-muted-foreground">Total Projects</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center gap-2 mt-1">
                    <LayoutGrid className="h-6 w-6 text-brand" />
                    {projects.length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="shadow-card border-border/60 bg-gradient-to-br from-card to-muted/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-xs uppercase font-semibold tracking-wider text-muted-foreground">Local AI Model</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center gap-2 mt-1 text-success">
                    <Database className="h-6 w-6" /> Qwen 3 (8B)
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="shadow-card border-border/60 bg-gradient-to-br from-card to-muted/20">
                <CardHeader className="pb-2">
                  <CardDescription className="text-xs uppercase font-semibold tracking-wider text-muted-foreground">Status</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center gap-2 mt-1 text-indigo-600">
                    <BarChart3 className="h-6 w-6" /> Active
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Project List */}
            {loadingProjects ? (
              <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                <Loader2 className="h-10 w-10 animate-spin text-brand mb-4" />
                <p className="text-sm font-medium">Retrieving saved blueprints...</p>
              </div>
            ) : projects.length === 0 ? (
              <Card className="border-dashed border-2 border-border p-12 text-center shadow-none bg-transparent">
                <div className="max-w-md mx-auto space-y-4">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-soft text-brand">
                    <Plus className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold">No blueprints created yet</h3>
                  <p className="text-sm text-muted-foreground">
                    Get started by using our multi-agent AI system to transform your ideas into fully structured developer packages.
                  </p>
                  <Button onClick={handleCreateNew} className="bg-brand text-brand-foreground gap-2">
                    <Plus className="h-4 w-4" /> Create your first blueprint
                  </Button>
                </div>
              </Card>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {projects.map((p) => (
                  <Card
                    key={p.id}
                    className="flex flex-col justify-between border-border/60 shadow-card hover:shadow-elevated transition-all duration-300 cursor-pointer group"
                    onClick={() => handleViewProject(p)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <CardTitle className="text-base font-semibold group-hover:text-brand transition-colors truncate">
                            {p.name}
                          </CardTitle>
                          <CardDescription className="text-xs font-medium text-brand mt-1 truncate">
                            {p.tech_stack}
                          </CardDescription>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-full shrink-0"
                          onClick={(e) => handleDeleteProject(p.id, e)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-3 mt-3 leading-relaxed">
                        {p.description || "No description provided."}
                      </p>
                    </CardHeader>
                    <CardContent className="pt-0 border-t border-border/40 mt-auto bg-muted/10 px-6 py-3 flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {new Date(p.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          title="Download ZIP"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-brand rounded-md"
                          onClick={(e) => handleDownloadZipForProject(p, e)}
                          disabled={!p.scaffold}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          title="Download PDF"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-brand rounded-md"
                          onClick={(e) => handleDownloadPdfForProject(p, e)}
                        >
                          <FileText className="h-4 w-4 text-red-600" />
                        </Button>
                        <Button
                          title="Download Word (DOCX)"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-brand rounded-md"
                          onClick={(e) => handleDownloadDocxForProject(p, e)}
                        >
                          <FileText className="h-4 w-4 text-blue-600" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: AI BLUEPRINT GENERATOR WORKSPACE */}
        {activeView === "create" && (
          <div className="grid gap-6 lg:grid-cols-12">
            
            {/* Left panel (Project Request Form & Live Progress) */}
            <div className="space-y-6 lg:col-span-4">
              <ProjectForm onGenerate={onGenerate} generating={generating} />
              <AgentProgress agents={agents} />
              <button
                className="w-full text-xs font-semibold py-2 rounded-lg border border-border text-muted-foreground hover:text-foreground transition-colors hover:bg-muted/30"
                onClick={handleTestLLM}
              >
                🛠 Verify Ollama Connection
              </button>
            </div>

            {/* Right panel (Workflow Results Tab Panel) */}
            <div className="space-y-6 lg:col-span-8">
              <ResultsTabs
                initialIdea={submittedIdea}
                savedContext={savedContextInput}
                savedScaffold={scaffold}
                onRequirementsUpdate={setCurrentRequirements}
                onArchitectureUpdate={setCurrentArchitecture}
                onDatabaseUpdate={setCurrentDatabase}
                onDocumentationUpdate={setCurrentDocumentation}
                onScaffoldGenerated={handleScaffoldGenerated}
              />
              <GeneratedFiles scaffold={scaffold} />
            </div>

          </div>
        )}

      </main>
      <Footer />
    </div>
  );
}
