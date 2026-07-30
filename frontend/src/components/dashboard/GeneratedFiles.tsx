import { useState } from "react";
import { Download, File, FileCode, FileText, Folder, Database as DbIcon, GitBranch, Package, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { generatedFiles } from "@/lib/blueprint-data";
import { ScaffoldResponse, downloadScaffoldZip } from "@/services/scaffold";

function iconFor(language?: string, name?: string) {
  if (name?.endsWith("/")) return Folder;
  if (language === "python") return FileCode;
  if (language === "typescript") return FileCode;
  if (language === "sql") return DbIcon;
  if (language === "yaml") return GitBranch;
  if (language === "markdown") return FileText;
  if (name?.endsWith(".md")) return FileText;
  if (name?.endsWith(".sql")) return DbIcon;
  if (name?.endsWith(".mmd")) return GitBranch;
  if (name?.endsWith(".ts") || name?.endsWith(".tsx")) return FileCode;
  return File;
}

function formatBytes(str: string): string {
  const bytes = new Blob([str]).size;
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

interface Props {
  scaffold?: ScaffoldResponse | null;
}

export function GeneratedFiles({ scaffold }: Props = {}) {
  const isLive = !!scaffold;
  const [downloadingZip, setDownloadingZip] = useState(false);

  const handleDownloadZip = async () => {
    if (!scaffold) return;
    setDownloadingZip(true);
    try {
      await downloadScaffoldZip(scaffold);
    } catch (err) {
      console.error("ZIP download failed:", err);
    } finally {
      setDownloadingZip(false);
    }
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            <Package className="h-4 w-4 text-brand" />
            Generated Files
          </CardTitle>
          <CardDescription>
            {isLive
              ? `${scaffold!.total_files} files assembled for "${scaffold!.project_name}".`
              : "Ready to download as a starter project."}
          </CardDescription>
        </div>
        <Button size="sm" onClick={handleDownloadZip} disabled={!isLive || downloadingZip}>
          {downloadingZip ? (
            <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
          ) : (
            <Download className="mr-1.5 h-4 w-4" />
          )}
          Download ZIP
        </Button>
      </CardHeader>
      <CardContent>
        {isLive ? (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {scaffold!.files.map((f) => {
              const Icon = iconFor(f.language, f.path);
              const filename = f.path.split("/").pop() || f.path;
              return (
                <div
                  key={f.path}
                  className="flex items-center gap-3 rounded-lg border border-border bg-background/60 p-3 transition-colors hover:bg-muted/40"
                  title={f.path}
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-soft text-brand shrink-0">
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium">{filename}</div>
                    <div className="text-xs text-muted-foreground truncate">{f.path}</div>
                    <div className="text-xs text-muted-foreground/60">{formatBytes(f.content)}</div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {generatedFiles.map((f) => {
              const Icon = iconFor(undefined, f.name);
              return (
                <div
                  key={f.name}
                  className="flex items-center gap-3 rounded-lg border border-border bg-background/60 p-3 transition-colors hover:bg-muted/40"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-soft text-brand">
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium">{f.name}</div>
                    <div className="text-xs text-muted-foreground">{f.size}</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
