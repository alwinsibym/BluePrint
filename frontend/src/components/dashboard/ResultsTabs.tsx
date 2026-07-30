import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RequirementsPanel } from "@/components/dashboard/RequirementsPanel";
import { ArchitecturePanel } from "@/components/dashboard/ArchitecturePanel";
import { DatabasePanel } from "@/components/dashboard/DatabasePanel";
import { DocumentationPanel } from "@/components/dashboard/DocumentationPanel";
import { ScaffoldPanel } from "@/components/dashboard/ScaffoldPanel";
import { RequirementsResponse } from "@/services/requirements";
import { ArchitectureResponse } from "@/services/architecture";
import { DatabaseResponse, ProjectContextInput } from "@/services/database";
import { DocumentationResponse } from "@/services/documentation";
import { ScaffoldResponse } from "@/services/scaffold";
import { exportBlueprintPdf } from "@/services/export";
import { sampleStructure } from "@/lib/blueprint-data";

function CodeBlock({ children, language }: { children: string; language?: string }) {
  return (
    <pre className="overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs leading-relaxed text-foreground">
      <code className={language ? `language-${language}` : undefined}>{children}</code>
    </pre>
  );
}

export function ResultsTabs({
  initialIdea,
  onScaffoldGenerated: externalOnScaffoldGenerated,
}: {
  initialIdea?: string | null;
  onScaffoldGenerated?: (data: ScaffoldResponse) => void;
} = {}) {
  const [requirements, setRequirements] = useState<RequirementsResponse | null>(null);
  const [architecture, setArchitecture] = useState<ArchitectureResponse | null>(null);
  const [database, setDatabase] = useState<DatabaseResponse | null>(null);
  const [documentation, setDocumentation] = useState<DocumentationResponse | null>(null);
  const [scaffold, setScaffold] = useState<ScaffoldResponse | null>(null);
  const [activeTab, setActiveTab] = useState("requirements");
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const projectContext: ProjectContextInput = {
    requirements,
    architecture,
    database,
    documentation,
  };

  const handleRequirementsGenerated = (data: RequirementsResponse) => {
    setRequirements(data);
    setActiveTab("architecture");
  };

  const handleArchitectureGenerated = (data: ArchitectureResponse) => {
    setArchitecture(data);
    setActiveTab("database");
  };

  const handleDatabaseGenerated = (data: DatabaseResponse) => {
    setDatabase(data);
    setActiveTab("docs");
  };

  const handleDocumentationGenerated = (data: DocumentationResponse) => {
    setDocumentation(data);
    setActiveTab("scaffold");
  };

  const handleScaffoldGenerated = (data: ScaffoldResponse) => {
    setScaffold(data);
    externalOnScaffoldGenerated?.(data);
  };

  const handleExportPdf = async () => {
    setExporting(true);
    setExportError(null);
    try {
      const blob = await exportBlueprintPdf(projectContext);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const projectName =
        requirements?.project_name?.toLowerCase().replace(/\s+/g, "_") ?? "blueprint";
      link.href = url;
      link.download = `${projectName}_blueprint.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setExportError(err?.message ?? "Failed to export PDF");
    } finally {
      setExporting(false);
    }
  };

  // Show the export button once we have at least requirements
  const canExport = requirements !== null;

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <CardTitle className="text-lg">Generated Blueprint</CardTitle>
          {canExport && (
            <div className="flex flex-col items-end gap-1">
              <Button
                id="export-pdf-btn"
                size="sm"
                variant="default"
                disabled={exporting}
                onClick={handleExportPdf}
                className="gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:from-indigo-700 hover:to-violet-700 shadow-md transition-all duration-200"
              >
                {exporting ? (
                  <>
                    <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                    Generating PDF…
                  </>
                ) : (
                  <>📄 Export PDF Report</>
                )}
              </Button>
              {exportError && (
                <span className="text-xs text-destructive">{exportError}</span>
              )}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="flex w-full flex-wrap justify-start gap-1 bg-muted/60">
            <TabsTrigger value="requirements">Requirements</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="database">Database</TabsTrigger>
            <TabsTrigger value="docs">Documentation</TabsTrigger>
            <TabsTrigger value="scaffold">🏗 Project</TabsTrigger>
            <TabsTrigger value="structure">Structure</TabsTrigger>
          </TabsList>

          <TabsContent value="requirements" className="mt-4">
            <RequirementsPanel
              initialIdea={initialIdea}
              onRequirementsGenerated={handleRequirementsGenerated}
            />
          </TabsContent>

          <TabsContent value="architecture" className="mt-4">
            <ArchitecturePanel
              requirements={requirements}
              architecture={architecture}
              onArchitectureGenerated={handleArchitectureGenerated}
            />
          </TabsContent>

          <TabsContent value="database" className="mt-4">
            <DatabasePanel
              context={projectContext}
              database={database}
              onDatabaseGenerated={handleDatabaseGenerated}
            />
          </TabsContent>

          <TabsContent value="docs" className="mt-4">
            <DocumentationPanel
              context={projectContext}
              documentation={documentation}
              onDocumentationGenerated={handleDocumentationGenerated}
            />
          </TabsContent>

          {/* Phase 7 – Scaffold / Project Generator tab */}
          <TabsContent value="scaffold" className="mt-4">
            <ScaffoldPanel
              context={projectContext}
              scaffold={scaffold}
              onScaffoldGenerated={handleScaffoldGenerated}
            />
          </TabsContent>

          <TabsContent value="structure" className="mt-4">
            <CodeBlock>{sampleStructure}</CodeBlock>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
