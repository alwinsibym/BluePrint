import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/site/Navbar";
import { Footer } from "@/components/site/Footer";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — Blueprint" },
      { name: "description", content: "Why Blueprint exists and who's behind it." },
      { property: "og:title", content: "About — Blueprint" },
      { property: "og:description", content: "The story and mission behind the Blueprint planning platform." },
    ],
  }),
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-16 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">About Blueprint</h1>
        <div className="prose prose-neutral mt-6 max-w-none text-muted-foreground">
          <p>
            Blueprint is a multi-agent planning platform for software teams. It exists to
            eliminate the blank-page problem that slows every new project: the days spent
            wiring boilerplate, drafting requirements, sketching schemas, and writing docs
            before the first real feature ships.
          </p>
          <p>
            The platform coordinates a small team of specialized AI agents — a
            requirements analyst, an architect, a database designer, a documentation
            author, and a scaffolding agent — that work together to turn a short prompt
            into a coherent, opinionated foundation.
          </p>
          <p>
            Blueprint is designed to run locally so your ideas and code never leave your
            machine. It's a tool for engineers who want to spend more time building and
            less time bootstrapping.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
