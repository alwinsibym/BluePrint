import { Check, Clock, Loader2 } from "lucide-react";
import type { Agent } from "@/lib/blueprint-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

function StatusBadge({ status }: { status: Agent["status"] }) {
  if (status === "completed")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
        <Check className="h-3 w-3" /> Completed
      </span>
    );
  if (status === "running")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-brand-soft px-2 py-0.5 text-xs font-medium text-brand">
        <Loader2 className="h-3 w-3 animate-spin" /> Running
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
      <Clock className="h-3 w-3" /> Waiting
    </span>
  );
}

export function AgentProgress({ agents }: { agents: Agent[] }) {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-lg">Agent Workflow</CardTitle>
        <CardDescription>Multi-agent pipeline status</CardDescription>
      </CardHeader>
      <CardContent>
        <ol className="relative space-y-4">
          {agents.map((agent, i) => (
            <li key={agent.id} className="relative pl-8">

              <span
                className={cn(
                  "absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full border text-xs font-medium",
                  agent.status === "completed" && "border-success bg-success text-primary-foreground",
                  agent.status === "running" && "border-brand bg-brand text-brand-foreground",
                  agent.status === "waiting" && "border-border bg-muted text-muted-foreground"
                )}
              >
                {agent.status === "completed" ? (
                  <Check className="h-3.5 w-3.5" />
                ) : agent.status === "running" ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  i + 1
                )}
              </span>
              {i < agents.length - 1 && (
                <span className="absolute left-3 top-8 h-full w-px bg-border" />
              )}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-sm font-medium">{agent.name}</div>
                  <div className="text-xs text-muted-foreground">{agent.description}</div>
                </div>
                <StatusBadge status={agent.status} />
              </div>
              {agent.status !== "waiting" && (
                <Progress value={agent.progress} className="mt-2 h-1.5" />
              )}
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
