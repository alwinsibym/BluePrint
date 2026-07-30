import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";
import { Features } from "@/components/site/Features";

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
        <section className="mx-auto max-w-7xl px-4 pt-16 pb-8 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Features</h1>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            A tour of what Blueprint's agents generate for every project.
          </p>
        </section>
        <Features />
      </main>
      <Footer />
    </div>
  );
}
