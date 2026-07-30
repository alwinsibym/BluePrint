import React, { useState } from "react";
import { generateDocumentation, DocumentationResponse } from "@/services/documentation";
import { ProjectContextInput } from "@/services/database";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, AlertCircle, RefreshCw, FileText, Copy, Download, Check } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { toast } from "sonner";

interface DocumentationPanelProps {
  context: ProjectContextInput;
  documentation: DocumentationResponse | null;
  onDocumentationGenerated: (doc: DocumentationResponse) => void;
}

export const DocumentationPanel: React.FC<DocumentationPanelProps> = ({
  context,
  documentation,
  onDocumentationGenerated,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const canGenerate = Boolean(context.requirements && context.architecture && context.database);

  const handleGenerate = async () => {
    if (!canGenerate) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await generateDocumentation(context);
      onDocumentationGenerated(result);
      toast.success("Documentation generated successfully!");
    } catch (err: any) {
      console.error("Failed to generate documentation:", err);
      setError(err.response?.data?.detail || err.message || "Failed to generate documentation. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, sectionName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionName);
    toast.success(`Copied ${sectionName} to clipboard!`);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const downloadMarkdown = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success(`Downloaded ${filename}!`);
  };

  if (!canGenerate) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Complete Context Required</h3>
        <p className="text-muted-foreground max-w-md mt-2">
          Please generate Requirements, Architecture, and Database design first before generating project documentation.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-muted-foreground animate-pulse">Generating README.md, setup guide, API docs & developer notes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="my-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Generation Failed</AlertTitle>
        <AlertDescription className="mt-2">
          {error}
          <div className="mt-4">
            <Button variant="outline" size="sm" onClick={handleGenerate}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!documentation) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <FileText className="w-12 h-12 text-primary/80 mb-4" />
        <h3 className="text-lg font-medium text-foreground mb-2">Ready to Document</h3>
        <p className="text-muted-foreground max-w-md mb-6">
          The AI will compile your entire ProjectContext into a production-grade README.md, setup guide, API documentation, and deployment notes.
        </p>
        <Button onClick={handleGenerate} size="lg">
          Generate Documentation
        </Button>
      </div>
    );
  }

  const sections = [
    { id: "overview", label: "Overview", content: documentation.project_overview, file: "overview.md" },
    { id: "readme", label: "README.md", content: documentation.readme_md, file: "README.md" },
    { id: "installation", label: "Installation", content: documentation.installation_guide, file: "setup.md" },
    { id: "api", label: "API Specs", content: documentation.api_documentation, file: "api.md" },
    { id: "structure", label: "Folder Structure", content: documentation.folder_structure_description, file: "structure.md" },
    { id: "deployment", label: "Deployment", content: documentation.deployment_notes, file: "deployment.md" },
    { id: "developer", label: "Developer Notes", content: documentation.developer_notes, file: "developer_notes.md" },
  ];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">Project Documentation</h2>
          <p className="text-muted-foreground">Comprehensive documentation ready for GitHub, setup, and deployment.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleGenerate}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Regenerate
        </Button>
      </div>

      <Tabs defaultValue="readme" className="w-full">
        <TabsList className="flex flex-wrap w-full justify-start gap-1 bg-muted/40 p-1">
          {sections.map((sec) => (
            <TabsTrigger key={sec.id} value={sec.id} className="text-xs">
              {sec.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {sections.map((sec) => (
          <TabsContent key={sec.id} value={sec.id} className="mt-4 space-y-3">
            <div className="flex items-center justify-between bg-muted/20 p-2 px-3 rounded-lg border border-border">
              <span className="text-xs font-mono font-semibold text-primary">{sec.file}</span>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="h-8 text-xs gap-1.5"
                  onClick={() => copyToClipboard(sec.content, sec.label)}
                >
                  {copiedSection === sec.label ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
                  Copy {sec.label}
                </Button>

                <Button 
                  variant="secondary" 
                  size="sm" 
                  className="h-8 text-xs gap-1.5"
                  onClick={() => downloadMarkdown(sec.content, sec.file)}
                >
                  <Download className="w-3.5 h-3.5" />
                  Download {sec.file}
                </Button>
              </div>
            </div>

            <div className="relative">
              <pre className="overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs font-mono leading-relaxed text-foreground whitespace-pre-wrap max-h-[500px]">
                <code>{sec.content}</code>
              </pre>
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};
