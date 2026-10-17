import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { Features } from "@/components/site/Features";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export const Route = createFileRoute("/features")({
  head: () => ({
    meta: [
      { title: "Features — Blueprint" },
      { name: "description", content: "Requirements, architecture, database, docs, and scaffolding — powered by AI agents." },
      { property: "og:title", content: "Features — Blueprint" },
      { property: "og:description", content: "Everything Blueprint's multi-agent planner can do for your next project." },
    ],
  }),
  component: FeaturesPage,
});

function FeaturesPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Page Hero */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center">
            <div className="h-[500px] w-[900px] rounded-full bg-brand-soft blur-3xl opacity-60" />
          </div>
          <div className="mx-auto max-w-7xl px-4 pt-20 pb-16 sm:px-6 lg:px-8 lg:pt-28">
            <div className="mx-auto max-w-2xl text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground shadow-card">
                <Sparkles className="h-3.5 w-3.5 text-brand" />
                What Blueprint generates
              </div>
              <h1 className="mt-5 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
                Everything your project needs,{" "}
                <span className="text-brand">instantly</span>
              </h1>
              <p className="mt-5 text-base text-muted-foreground sm:text-lg">
                Blueprint's agents collaborate so you skip the blank-page problem and go straight to building. Here's exactly what gets generated.
              </p>
            </div>
          </div>
        </section>

        {/* Feature cards — reuses the shared component used on the home page */}
        <Features />

        {/* CTA */}
        <section className="border-t border-border/60">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="rounded-2xl border border-border bg-card p-10 shadow-elevated text-center">
              <h2 className="text-3xl font-semibold tracking-tight">
                See it in action
              </h2>
              <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
                Paste a prompt and watch Blueprint generate all seven artifacts in real time — for free.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Button asChild size="lg" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                  <Link to="/signup">
                    Try Blueprint free <ArrowRight className="ml-1.5 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/documentation">Read the docs</Link>
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
