import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { LogOut } from "lucide-react";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { ProjectForm } from "@/components/dashboard/ProjectForm";
import { AgentProgress } from "@/components/dashboard/AgentProgress";
import { ResultsTabs } from "@/components/dashboard/ResultsTabs";
import { GeneratedFiles } from "@/components/dashboard/GeneratedFiles";
import { initialAgents, type Agent } from "@/lib/blueprint-data";
import { generateBlueprint, type GenerateResponse } from "@/services/api";
import { testLLM } from "@/services/llm";
import { ScaffoldResponse } from "@/services/scaffold";
import { useAuth } from "@/lib/AuthContext";
import { Button } from "@/components/ui/button";
import { supabase } from "@/lib/supabase";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Blueprint" },
      { name: "description", content: "Generate a full project blueprint with Blueprint's multi-agent planner." },
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
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [generating, setGenerating] = useState(false);
  const [backendResponse, setBackendResponse] = useState<GenerateResponse | null>(null);
  const [scaffold, setScaffold] = useState<ScaffoldResponse | null>(null);
  const [submittedIdea, setSubmittedIdea] = useState<string | null>(null);

  const onGenerate = async (name: string, description: string, techStack: string) => {
    setGenerating(true);
    setBackendResponse(null);
    setSubmittedIdea(`${name}: ${description} (Tech Stack: ${techStack})`);
    setAgents((a) => a.map((x) => ({ ...x, status: "waiting", progress: 0 })));

    try {
      const response = await generateBlueprint({ name, description, tech_stack: techStack });

      let step = 0;
      const advance = () => {
        setAgents((current) => {
          const next = [...current];
          if (step > 0) {
            next[step - 1] = { ...next[step - 1], status: "completed", progress: 100 };
          }
          if (step < next.length) {
            next[step] = { ...next[step], status: "running", progress: 40 };
          }
          return next;
        });
        step += 1;
        if (step <= initialAgents.length) {
          setTimeout(advance, 700);
        } else {
          setGenerating(false);
          setBackendResponse(response);
          toast.success("Blueprint backend is connected successfully!");
        }
      };

      setTimeout(advance, 400);
    } catch (error) {
      console.error("Failed to generate blueprint:", error);
      setGenerating(false);
      toast.error("Failed to connect to the backend. Is the server running?");
    }
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

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out successfully.");
    navigate({ to: "/" });
  };

  return (
    <div className="flex min-h-screen flex-col bg-muted/20">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              {user?.user_metadata?.full_name
                ? `Welcome, ${user.user_metadata.full_name} — draft, review, and export a complete project blueprint.`
                : "Draft, review, and export a complete project blueprint."}
            </p>
          </div>
          <Button
            id="dashboard-signout-btn"
            variant="ghost"
            size="sm"
            onClick={handleSignOut}
            className="gap-2 text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-12">
          {/* Left panel */}
          <div className="space-y-6 lg:col-span-4">
            <ProjectForm onGenerate={onGenerate} generating={generating} />
            <AgentProgress agents={agents} />
            <button className="btn-primary mt-4" onClick={handleTestLLM}>
              Test LLM
            </button>
          </div>

          {/* Right panel */}
          <div className="space-y-6 lg:col-span-8">
            {backendResponse && (
              <div className="rounded-xl border border-success/20 bg-success/5 p-5 text-card-foreground shadow-card animate-in fade-in slide-in-from-top-4 duration-300">
                <div className="flex items-center gap-2.5 font-semibold text-success">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-success" />
                  </span>
                  Backend Connected Successfully
                </div>
                <div className="mt-2 text-sm text-muted-foreground">
                  <p className="mb-2"><strong>Message:</strong> {backendResponse.message}</p>
                  <p>
                    <strong>Generated Project:</strong>{" "}
                    <span className="text-foreground font-medium">{backendResponse.project.name}</span>
                  </p>
                  <p className="text-xs mt-1 italic">Description: {backendResponse.project.description}</p>
                </div>
              </div>
            )}

            {/* Main agent workflow tabs – passes scaffold state up via callback */}
            <ResultsTabs initialIdea={submittedIdea} onScaffoldGenerated={setScaffold} />

            {/* Generated file grid – live when scaffold is available */}
            <GeneratedFiles scaffold={scaffold} />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
