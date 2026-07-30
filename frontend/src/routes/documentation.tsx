import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, PlayCircle, Wrench, Rocket } from "lucide-react";

export const Route = createFileRoute("/documentation")({
  head: () => ({
    meta: [
      { title: "Documentation — Blueprint" },
      { name: "description", content: "Guides for installing, running, and extending Blueprint." },
      { property: "og:title", content: "Documentation — Blueprint" },
      { property: "og:description", content: "Get started with Blueprint's multi-agent planning platform." },
    ],
  }),
  component: DocumentationPage,
});

const sections = [
  { icon: PlayCircle, title: "Quick Start", desc: "Install the CLI and generate your first blueprint in under two minutes." },
  { icon: BookOpen, title: "Concepts", desc: "How the agent pipeline is orchestrated and how artifacts flow between steps." },
  { icon: Wrench, title: "Configuration", desc: "Choose local models, tune prompts, and customize scaffolding templates." },
  { icon: Rocket, title: "Deploying Output", desc: "Ship the generated projects to Vercel, Fly.io, or your own infrastructure." },
];

function DocumentationPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-16 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Documentation</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Everything you need to install Blueprint, run the pipeline, and customize outputs.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {sections.map((s) => (
            <Card key={s.title} className="shadow-card">
              <CardHeader>
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-soft text-brand">
                  <s.icon className="h-5 w-5" />
                </span>
                <CardTitle className="mt-3 text-lg">{s.title}</CardTitle>
                <CardDescription>{s.desc}</CardDescription>
              </CardHeader>
              <CardContent />
            </Card>
          ))}
        </div>

        <div className="mt-10 rounded-xl border border-border bg-card p-6 shadow-card">
          <h2 className="text-lg font-semibold">Install</h2>
          <pre className="mt-3 overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs">
{`# Install Blueprint CLI
curl -fsSL https://get.blueprint.dev | sh

# Generate your first project
blueprint new my-app --stack react-fastapi`}
          </pre>
        </div>
      </main>
      <Footer />
    </div>
  );
}
