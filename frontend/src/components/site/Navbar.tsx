import { Link, useNavigate } from "@tanstack/react-router";
import { Blocks, Menu, X, LogOut, LayoutDashboard, ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/AuthContext";
import { toast } from "sonner";

const links = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
  { to: "/documentation", label: "Documentation" },
  { to: "/about", label: "About" },
] as const;

function UserAvatar({ name, email }: { name?: string; email?: string }) {
  const initials = name
    ? name
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : (email?.[0]?.toUpperCase() ?? "U");
  return (
    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-brand-foreground text-xs font-semibold select-none">
      {initials}
    </span>
  );
}

function UserMenu({ onSignOut }: { onSignOut: () => void }) {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const name = user?.user_metadata?.full_name as string | undefined;
  const email = user?.email;

  return (
    <div className="relative" ref={ref}>
      <button
        id="navbar-user-menu-btn"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-lg border border-border px-2 py-1 hover:bg-muted/60 transition-colors"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <UserAvatar name={name} email={email} />
        <span className="hidden max-w-[120px] truncate text-sm font-medium sm:block">
          {name ?? email}
        </span>
        <ChevronDown className={`h-3.5 w-3.5 text-muted-foreground transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-52 rounded-xl border border-border bg-card shadow-elevated animate-in fade-in slide-in-from-top-2 duration-150 z-50">
          {/* User info */}
          <div className="px-4 py-3 border-b border-border">
            <p className="text-sm font-medium truncate">{name ?? "User"}</p>
            <p className="text-xs text-muted-foreground truncate mt-0.5">{email}</p>
          </div>
          {/* Menu items */}
          <div className="p-1">
            <Link
              to="/dashboard"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 w-full rounded-lg px-3 py-2 text-sm text-foreground hover:bg-muted/60 transition-colors"
            >
              <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
              Dashboard
            </Link>
            <button
              id="navbar-signout-btn"
              onClick={() => { setOpen(false); onSignOut(); }}
              className="flex items-center gap-2 w-full rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export function Navbar() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { user, signOut, loading } = useAuth();
  const isSignedIn = !!user;

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out successfully.");
    navigate({ to: "/" });
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-brand-foreground">
            <Blocks className="h-4 w-4" />
          </span>
          <span className="text-base font-semibold tracking-tight">Blueprint</span>
        </Link>

        {/* Desktop nav links */}
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              activeProps={{ className: "text-foreground bg-muted" }}
              activeOptions={{ exact: l.to === "/" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        {/* Desktop auth buttons */}
        <div className="hidden items-center gap-2 md:flex">
          {loading ? (
            <div className="h-8 w-20 rounded-lg bg-muted animate-pulse" />
          ) : isSignedIn ? (
            <>
              <Button asChild variant="ghost" size="sm" className="gap-1.5">
                <Link to="/dashboard">
                  <LayoutDashboard className="h-4 w-4" />
                  Dashboard
                </Link>
              </Button>
              <UserMenu onSignOut={handleSignOut} />
            </>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link to="/login" id="navbar-signin-btn">Sign in</Link>
              </Button>
              <Button asChild size="sm" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                <Link to="/signup" id="navbar-signup-btn">Sign up free</Link>
              </Button>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="border-t border-border md:hidden">
          <nav className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-3">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
                activeProps={{ className: "text-foreground bg-muted" }}
                activeOptions={{ exact: l.to === "/" }}
              >
                {l.label}
              </Link>
            ))}
            <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
              {isSignedIn ? (
                <>
                  <Button asChild size="sm">
                    <Link to="/dashboard" onClick={() => setOpen(false)}>
                      <LayoutDashboard className="mr-1.5 h-4 w-4" />
                      Dashboard
                    </Link>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { setOpen(false); handleSignOut(); }}
                    className="gap-2 text-destructive border-destructive/30 hover:bg-destructive/10"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </Button>
                </>
              ) : (
                <>
                  <Button asChild size="sm" variant="outline">
                    <Link to="/login" onClick={() => setOpen(false)}>Sign in</Link>
                  </Button>
                  <Button asChild size="sm" className="bg-brand hover:bg-brand/90 text-brand-foreground">
                    <Link to="/signup" onClick={() => setOpen(false)}>Sign up free</Link>
                  </Button>
                </>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
