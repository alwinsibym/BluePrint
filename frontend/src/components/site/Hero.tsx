import { Link } from "@tanstack/react-router";
import { ArrowRight, Sparkles, FileCode, Database, GitBranch, FileText, Boxes } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/AuthContext";

export function Hero() {
  const { user } = useAuth();
  return (
    <section className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center">
        <div className="h-[500px] w-[900px] rounded-full bg-brand-soft blur-3xl opacity-60" />
      </div>
      <div className="mx-auto max-w-7xl px-4 pt-20 pb-16 sm:px-6 lg:px-8 lg:pt-28">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground shadow-card">
              <Sparkles className="h-3.5 w-3.5 text-brand" />
              Multi-agent planning, in seconds
            </div>
            <h1 className="mt-5 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Transform your software idea into a{" "}
              <span className="text-brand">project foundation</span>
            </h1>
            <p className="mt-5 max-w-xl text-base text-muted-foreground sm:text-lg">
              Blueprint orchestrates AI agents to draft requirements, architecture,
              database schemas, docs, and a scaffolded repo — all from a single prompt.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button asChild size="lg" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                <Link to={user ? "/dashboard" : "/signup"}>
                  Get Started <ArrowRight className="ml-1.5 h-4 w-4" />
                </Link>
              </Button>
              {!user && (
                <Button asChild size="lg" variant="outline">
                  <Link to="/login">Sign in</Link>
                </Button>
              )}
              {user && (
                <Button asChild size="lg" variant="outline">
                  <Link to="/documentation">Read the docs</Link>
                </Button>
              )}
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
              <span>Free forever</span>
              <span className="h-1 w-1 rounded-full bg-border" />
              <span>Local AI processing</span>
              <span className="h-1 w-1 rounded-full bg-border" />
              <span>Export as ZIP</span>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-2xl border border-border bg-card p-4 shadow-elevated">
              <div className="flex items-center gap-1.5 border-b border-border pb-3">
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="h-2.5 w-2.5 rounded-full bg-muted" />
                <span className="ml-3 text-xs text-muted-foreground">blueprint / new-project</span>
              </div>
              <div className="grid gap-3 pt-4 sm:grid-cols-2">
                {[
                  { icon: FileText, label: "Requirements", meta: "12 items" },
                  { icon: Boxes, label: "Architecture", meta: "3 services" },
                  { icon: Database, label: "Database", meta: "8 tables" },
                  { icon: GitBranch, label: "ER Diagram", meta: "auto" },
                  { icon: FileCode, label: "Docs", meta: "README.md" },
                  { icon: Sparkles, label: "Scaffold", meta: "ready" },
                ].map((c) => (
                  <div
                    key={c.label}
                    className="flex items-center gap-3 rounded-lg border border-border bg-background/60 p-3"
                  >
                    <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-soft text-brand">
                      <c.icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0">
                      <div className="text-sm font-medium">{c.label}</div>
                      <div className="text-xs text-muted-foreground">{c.meta}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-lg border border-border bg-background/60 p-3">
                <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>Generating blueprint…</span>
                  <span>78%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                  <div className="h-full w-[78%] rounded-full bg-brand" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
