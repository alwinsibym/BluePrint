import { Boxes, Database, FileCode, FileText, GitBranch, Sparkles, Cpu } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: FileText,
    title: "Requirements Generation",
    desc: "Turn a rough prompt into structured functional and non-functional requirements.",
  },
  {
    icon: Boxes,
    title: "Software Architecture",
    desc: "Get service boundaries, tech decisions, and system diagrams tailored to your stack.",
  },
  {
    icon: Database,
    title: "Database Design",
    desc: "Normalized schemas, relationships, and SQL migrations ready to run.",
  },
  {
    icon: GitBranch,
    title: "ER Diagrams",
    desc: "Auto-generated Mermaid diagrams for entities, keys, and relationships.",
  },
  {
    icon: FileCode,
    title: "Documentation",
    desc: "README, setup guides, and architecture docs written for your team.",
  },
  {
    icon: Sparkles,
    title: "Project Scaffolding",
    desc: "A working starter repo with folder structure and dependencies pre-wired.",
  },
  {
    icon: Cpu,
    title: "Local AI Processing",
    desc: "Run privately on your own hardware — nothing leaves your machine.",
  },
];

export function Features() {
  return (
    <section id="features" className="border-t border-border/60 bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Everything you need to start a project right
          </h2>
          <p className="mt-3 text-muted-foreground">
            Blueprint's agents collaborate so you skip the blank-page problem and go
            straight to building.
          </p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <Card key={f.title} className="border-border/70 shadow-card transition-shadow hover:shadow-elevated">
              <CardHeader>
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-soft text-brand">
                  <f.icon className="h-5 w-5" />
                </span>
                <CardTitle className="mt-3 text-lg">{f.title}</CardTitle>
                <CardDescription>{f.desc}</CardDescription>
              </CardHeader>
              <CardContent />
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
