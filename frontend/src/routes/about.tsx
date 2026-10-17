import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Blocks,
  Sparkles,
  Target,
  Users,
  Zap,
  ArrowRight,
  CheckCircle2,
  GitBranch,
  FileCode,
  Database,
  Cpu,
} from "lucide-react";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — Blueprint" },
      { name: "description", content: "Learn about Blueprint — the multi-agent planning platform built for software teams." },
      { property: "og:title", content: "About — Blueprint" },
      { property: "og:description", content: "The story and mission behind Blueprint." },
    ],
  }),
  component: AboutPage,
});

const milestones = [
  { icon: Target, title: "The Problem", desc: "Every new software project starts the same way: days lost setting up boilerplate, drafting requirements, and writing docs — before a single feature ships." },
  { icon: Sparkles, title: "The Solution", desc: "Blueprint orchestrates a pipeline of AI agents to do all of that for you in seconds, from a single plain-English prompt." },
  { icon: Zap, title: "The Result", desc: "Your team starts building features from day one, with a fully scaffolded repo, schema, architecture, and documentation already in place." },
];

const values = [
  { icon: Cpu, title: "Local-first", desc: "All AI processing runs on your own hardware. Nothing leaves your machine." },
  { icon: Users, title: "Team-oriented", desc: "Output is structured for teams — requirements, diagrams, and docs your whole org can read." },
  { icon: GitBranch, title: "Open & Extensible", desc: "Swap models, tweak prompts, and extend templates to fit your workflow." },
  { icon: FileCode, title: "Production-ready Output", desc: "Not a prototype. Every artifact is formatted for immediate use in CI/CD pipelines." },
  { icon: Database, title: "Schema-first Design", desc: "Database design is treated as a first-class citizen, not an afterthought." },
  { icon: CheckCircle2, title: "No Lock-in", desc: "Export as ZIP. Own your output. Blueprint is a tool, not a platform dependency." },
];

function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center">
            <div className="h-[500px] w-[900px] rounded-full bg-brand-soft blur-3xl opacity-60" />
          </div>
          <div className="mx-auto max-w-7xl px-4 pt-20 pb-16 sm:px-6 lg:px-8 lg:pt-28">
            <div className="mx-auto max-w-2xl text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground shadow-card">
                <Blocks className="h-3.5 w-3.5 text-brand" />
                Our story &amp; mission
              </div>
              <h1 className="mt-5 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
                Built to eliminate the{" "}
                <span className="text-brand">blank-page problem</span>
              </h1>
              <p className="mt-5 text-base text-muted-foreground sm:text-lg">
                Blueprint is a multi-agent planning platform for software teams. We believe the first week of any project should be spent building features, not scaffolding.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Button asChild size="lg" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                  <Link to="/features">
                    See what it does <ArrowRight className="ml-1.5 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/documentation">Read the docs</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* How we got here */}
        <section className="border-t border-border/60 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">How Blueprint works</h2>
              <p className="mt-3 text-muted-foreground">
                Three steps that compress a week of setup into seconds.
              </p>
            </div>
            <div className="mt-12 grid gap-6 sm:grid-cols-3">
              {milestones.map((m, i) => (
                <Card key={m.title} className="border-border/70 shadow-card">
                  <CardHeader>
                    <div className="flex items-start gap-4">
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
                        <m.icon className="h-5 w-5" />
                      </span>
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-border text-xs font-semibold text-muted-foreground">
                        {i + 1}
                      </span>
                    </div>
                    <CardTitle className="mt-3 text-lg">{m.title}</CardTitle>
                    <CardDescription>{m.desc}</CardDescription>
                  </CardHeader>
                  <CardContent />
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Values */}
        <section>
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                What we stand for
              </h2>
              <p className="mt-3 text-muted-foreground">
                Principles that shape every decision we make.
              </p>
            </div>
            <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {values.map((v) => (
                <Card key={v.title} className="border-border/70 shadow-card transition-shadow hover:shadow-elevated">
                  <CardHeader>
                    <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-soft text-brand">
                      <v.icon className="h-5 w-5" />
                    </span>
                    <CardTitle className="mt-3 text-lg">{v.title}</CardTitle>
                    <CardDescription>{v.desc}</CardDescription>
                  </CardHeader>
                  <CardContent />
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Banner */}
        <section className="border-t border-border/60 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="rounded-2xl border border-border bg-card p-10 shadow-elevated text-center">
              <h2 className="text-3xl font-semibold tracking-tight">
                Ready to skip the setup?
              </h2>
              <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
                Sign up and generate your first blueprint in under two minutes — free, no credit card required.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Button asChild size="lg" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                  <Link to="/signup">
                    Get started free <ArrowRight className="ml-1.5 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/features">Explore features</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
