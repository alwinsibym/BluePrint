import { Blocks, Github } from "lucide-react";
import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-brand-foreground">
                <Blocks className="h-4 w-4" />
              </span>
              <span className="text-base font-semibold tracking-tight">Blueprint</span>
            </Link>
            <p className="mt-3 max-w-sm text-sm text-muted-foreground">
              A multi-agent software planning platform that turns any idea into a
              development-ready project foundation.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Technologies</h4>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li>React + TypeScript</li>
              <li>Tailwind CSS</li>
              <li>shadcn/ui</li>
              <li>TanStack Start</li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Resources</h4>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link to="/documentation" className="text-muted-foreground hover:text-foreground">Documentation</Link>
              </li>
              <li>
                <Link to="/features" className="text-muted-foreground hover:text-foreground">Features</Link>
              </li>
              <li>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-muted-foreground hover:text-foreground"
                >
                  <Github className="h-3.5 w-3.5" /> GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 text-xs text-muted-foreground sm:flex-row">
          <p>© {new Date().getFullYear()} Blueprint. All rights reserved.</p>
          <p>From idea to project foundation.</p>
        </div>
      </div>
    </footer>
  );
}
