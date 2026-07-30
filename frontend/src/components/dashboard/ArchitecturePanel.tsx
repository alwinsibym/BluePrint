import React, { useState } from "react";
import { generateArchitecture, ArchitectureResponse } from "@/services/architecture";
import { RequirementsResponse } from "@/services/requirements";
import { Button } from "@/components/ui/button";
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ArchitecturePanelProps {
  requirements: RequirementsResponse | null;
  architecture: ArchitectureResponse | null;
  onArchitectureGenerated: (arch: ArchitectureResponse) => void;
}

export const ArchitecturePanel: React.FC<ArchitecturePanelProps> = ({ 
  requirements, 
  architecture,
  onArchitectureGenerated
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!requirements) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const result = await generateArchitecture(requirements);
      onArchitectureGenerated(result);
    } catch (err: any) {
      console.error("Failed to generate architecture:", err);
      setError(err.response?.data?.detail || err.message || "Failed to generate architecture. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!requirements) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Requirements Needed</h3>
        <p className="text-muted-foreground max-w-md mt-2">
          Please generate the project requirements first before generating the architecture.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-muted-foreground animate-pulse">Designing software architecture...</p>
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

  if (!architecture) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <h3 className="text-lg font-medium text-foreground mb-2">Ready to Design</h3>
        <p className="text-muted-foreground max-w-md mb-6">
          Using the generated requirements, the AI will now design the high-level architecture, 
          folder structure, and component breakdown.
        </p>
        <Button onClick={handleGenerate} size="lg">
          Generate Architecture
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">Architecture Design</h2>
          <p className="text-muted-foreground">High-level software architecture and components.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleGenerate}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Regenerate
        </Button>
      </div>

      <Accordion type="multiple" defaultValue={["overview", "folders", "components", "dataflow"]} className="w-full">
        
        <AccordionItem value="overview">
          <AccordionTrigger className="text-lg font-medium">High-Level Architecture</AccordionTrigger>
          <AccordionContent>
            <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground">
              <p>{architecture.high_level_architecture}</p>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="folders">
          <AccordionTrigger className="text-lg font-medium">Folder Structure</AccordionTrigger>
          <AccordionContent>
            <div className="bg-muted/50 p-4 rounded-md border border-border">
              <ul className="space-y-2 font-mono text-sm">
                {architecture.folder_structure.map((path, idx) => (
                  <li key={idx} className="flex items-center text-muted-foreground">
                    <span className="text-primary/70 mr-2">📁</span> {path}
                  </li>
                ))}
              </ul>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="components">
          <AccordionTrigger className="text-lg font-medium">Component Breakdown</AccordionTrigger>
          <AccordionContent>
            <div className="grid gap-4 md:grid-cols-2">
              {architecture.component_breakdown.map((comp, idx) => (
                <div key={idx} className="bg-card p-4 rounded-lg border border-border/50 shadow-sm">
                  <h4 className="font-semibold text-foreground flex items-center mb-2">
                    <span className="w-2 h-2 rounded-full bg-primary mr-2"></span>
                    {comp.name}
                  </h4>
                  <p className="text-sm text-muted-foreground mb-4">{comp.description}</p>
                  
                  {comp.dependencies.length > 0 && (
                    <div>
                      <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider block mb-2">
                        Dependencies
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {comp.dependencies.map((dep, dIdx) => (
                          <Badge key={dIdx} variant="secondary" className="text-xs bg-secondary/50">
                            {dep}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="dataflow">
          <AccordionTrigger className="text-lg font-medium">Data Flow</AccordionTrigger>
          <AccordionContent>
            <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground">
              <p>{architecture.data_flow}</p>
            </div>
          </AccordionContent>
        </AccordionItem>

      </Accordion>
    </div>
  );
};
