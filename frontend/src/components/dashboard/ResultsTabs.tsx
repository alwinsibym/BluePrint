import { useState, useEffect } from "react";
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
import { exportBlueprintDocx } from "@/services/export_docx";
import { sampleStructure } from "@/lib/blueprint-data";

function CodeBlock({ children, language }: { children: string; language?: string }) {
  return (
    <pre className="overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs leading-relaxed text-foreground">
      <code className={language ? `language-${language}` : undefined}>{children}</code>
    </pre>
  );
}

interface ResultsTabsProps {
  initialIdea?: string | null;
  onScaffoldGenerated?: (data: ScaffoldResponse) => void;
  // Allow loading a saved context directly
  savedContext?: ProjectContextInput | null;
  savedScaffold?: ScaffoldResponse | null;
  onRequirementsUpdate?: (data: RequirementsResponse) => void;
  onArchitectureUpdate?: (data: ArchitectureResponse) => void;
  onDatabaseUpdate?: (data: DatabaseResponse) => void;
  onDocumentationUpdate?: (data: DocumentationResponse) => void;
}

export function ResultsTabs({
  initialIdea,
  onScaffoldGenerated: externalOnScaffoldGenerated,
  savedContext,
  savedScaffold,
  onRequirementsUpdate,
  onArchitectureUpdate,
  onDatabaseUpdate,
  onDocumentationUpdate,
}: ResultsTabsProps = {}) {
  const [requirements, setRequirements] = useState<RequirementsResponse | null>(null);
  const [architecture, setArchitecture] = useState<ArchitectureResponse | null>(null);
  const [database, setDatabase] = useState<DatabaseResponse | null>(null);
  const [documentation, setDocumentation] = useState<DocumentationResponse | null>(null);
  const [scaffold, setScaffold] = useState<ScaffoldResponse | null>(null);
  const [activeTab, setActiveTab] = useState("requirements");
  const [exporting, setExporting] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Sync state if loading a saved project context
  useEffect(() => {
    if (savedContext) {
      if (savedContext.requirements) setRequirements(savedContext.requirements);
      if (savedContext.architecture) setArchitecture(savedContext.architecture);
      if (savedContext.database) setDatabase(savedContext.database);
      if (savedContext.documentation) setDocumentation(savedContext.documentation);

      // Auto-advance active tab to the latest completed step
      if (savedContext.documentation) setActiveTab("docs");
      else if (savedContext.database) setActiveTab("database");
      else if (savedContext.architecture) setActiveTab("architecture");
      else if (savedContext.requirements) setActiveTab("requirements");
    } else {
      setRequirements(null);
      setArchitecture(null);
      setDatabase(null);
      setDocumentation(null);
    }
  }, [savedContext]);

  useEffect(() => {
    if (savedScaffold) {
      setScaffold(savedScaffold);
      setActiveTab("scaffold");
    } else {
      setScaffold(null);
    }
  }, [savedScaffold]);

  const projectContext: ProjectContextInput = {
    requirements,
    architecture,
    database,
    documentation,
  };

  const handleRequirementsGenerated = (data: RequirementsResponse) => {
    setRequirements(data);
    onRequirementsUpdate?.(data);
  };

  const handleArchitectureGenerated = (data: ArchitectureResponse) => {
    setArchitecture(data);
    onArchitectureUpdate?.(data);
  };

  const handleDatabaseGenerated = (data: DatabaseResponse) => {
    setDatabase(data);
    onDatabaseUpdate?.(data);
  };

  const handleDocumentationGenerated = (data: DocumentationResponse) => {
    setDocumentation(data);
    onDocumentationUpdate?.(data);
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

  const handleExportDocx = async () => {
    setExportingDocx(true);
    setExportError(null);
    try {
      const blob = await exportBlueprintDocx(projectContext);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const projectName =
        requirements?.project_name?.toLowerCase().replace(/\s+/g, "_") ?? "blueprint";
      link.href = url;
      link.download = `${projectName}_blueprint.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setExportError(err?.message ?? "Failed to export Word Document (DOCX)");
    } finally {
      setExportingDocx(false);
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
              <div className="flex items-center gap-2">
                <Button
                  id="export-pdf-btn"
                  size="sm"
                  variant="default"
                  disabled={exporting}
                  onClick={handleExportPdf}
                  className="gap-2 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md transition-all duration-200"
                >
                  {exporting ? (
                    <>
                      <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                      PDF…
                    </>
                  ) : (
                    <>📄 Export PDF</>
                  )}
                </Button>
                <Button
                  id="export-docx-btn"
                  size="sm"
                  variant="outline"
                  disabled={exportingDocx}
                  onClick={handleExportDocx}
                  className="gap-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 shadow-sm transition-all duration-200"
                >
                  {exportingDocx ? (
                    <>
                      <span className="animate-spin inline-block w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full" />
                      Word…
                    </>
                  ) : (
                    <>📝 Export Word</>
                  )}
                </Button>
              </div>
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
              requirements={requirements}
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
