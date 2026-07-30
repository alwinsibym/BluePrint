import React, { useState, useEffect, useRef } from "react";
import mermaid from "mermaid";
import { generateDatabase, DatabaseResponse, ProjectContextInput } from "@/services/database";
import { Button } from "@/components/ui/button";
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Loader2, AlertCircle, RefreshCw, Database as DatabaseIcon, Code2, Layers } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface DatabasePanelProps {
  context: ProjectContextInput;
  database: DatabaseResponse | null;
  onDatabaseGenerated: (db: DatabaseResponse) => void;
}

// Sub-component for rendering Mermaid ER Diagram with safe error boundary fallback
function MermaidDiagram({ chart }: { chart: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (!chart) return;

    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      securityLevel: "loose",
    });

    const renderChart = async () => {
      try {
        const id = `mermaid-er-${Math.random().toString(36).substring(2, 9)}`;
        // Clean markdown fences if any are present in raw string
        const cleanedChart = chart.replace(/```(?:mermaid)?/g, "").trim();
        const { svg: renderedSvg } = await mermaid.render(id, cleanedChart);
        if (isMounted) {
          setSvg(renderedSvg);
          setRenderError(null);
        }
      } catch (err: any) {
        console.error("Mermaid render error:", err);
        if (isMounted) {
          setRenderError(err.message || "Failed to render ER Diagram visually.");
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  if (renderError) {
    return (
      <div className="space-y-2">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Diagram Visualizer Fallback</AlertTitle>
          <AlertDescription className="text-xs">
            Could not visually render the Mermaid diagram syntax. Raw syntax is displayed below.
          </AlertDescription>
        </Alert>
        <pre className="overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs font-mono">
          <code>{chart}</code>
        </pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="flex items-center justify-center h-48 bg-muted/20 rounded-lg border border-border">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      className="p-4 bg-muted/20 rounded-lg border border-border overflow-x-auto flex justify-center"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

export const DatabasePanel: React.FC<DatabasePanelProps> = ({
  context,
  database,
  onDatabaseGenerated,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canGenerate = Boolean(context.requirements && context.architecture);

  const handleGenerate = async () => {
    if (!canGenerate) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await generateDatabase(context);
      onDatabaseGenerated(result);
    } catch (err: any) {
      console.error("Failed to generate database design:", err);
      setError(err.response?.data?.detail || err.message || "Failed to generate database schema. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!canGenerate) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Requirements & Architecture Needed</h3>
        <p className="text-muted-foreground max-w-md mt-2">
          Please generate both Project Requirements and Software Architecture before proceeding to Database design.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-muted-foreground animate-pulse">Designing database entities, SQLite schema & ER diagram...</p>
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

  if (!database) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <DatabaseIcon className="w-12 h-12 text-primary/80 mb-4" />
        <h3 className="text-lg font-medium text-foreground mb-2">Ready for Database Design</h3>
        <p className="text-muted-foreground max-w-md mb-6">
          Using your Project Context (Requirements + Architecture), the AI will derive entities, relationships, SQLite schema, and a Mermaid ER Diagram.
        </p>
        <Button onClick={handleGenerate} size="lg">
          Generate Database Design
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">Database Design</h2>
          <p className="text-muted-foreground">Entities, relationships, SQLite DDL, and ER Diagram.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleGenerate}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Regenerate
        </Button>
      </div>

      <Accordion type="multiple" defaultValue={["overview", "entities", "relationships", "diagram", "sql"]} className="w-full">
        
        {/* Section 1: Overview & Notes */}
        <AccordionItem value="overview">
          <AccordionTrigger className="text-lg font-medium">Database Overview</AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4">
              <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground">
                <p>{database.database_overview}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-muted/30 p-3 rounded-lg border border-border">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-1">Normalization Notes</h4>
                  <p className="text-xs text-muted-foreground">{database.normalization_notes}</p>
                </div>
                <div className="bg-muted/30 p-3 rounded-lg border border-border">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-1">Table Summary</h4>
                  <p className="text-xs text-muted-foreground">{database.table_summary}</p>
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Section 2: Entities */}
        <AccordionItem value="entities">
          <AccordionTrigger className="text-lg font-medium">
            Entities & Tables ({database.entities.length})
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid gap-4 md:grid-cols-2">
              {database.entities.map((entity, idx) => (
                <div key={idx} className="bg-card p-4 rounded-lg border border-border/60 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-foreground flex items-center text-base">
                      <Layers className="w-4 h-4 text-primary mr-2" />
                      {entity.name}
                    </h4>
                    <Badge variant="outline" className="text-xs">
                      PK: {entity.primary_key}
                    </Badge>
                  </div>

                  <p className="text-xs text-muted-foreground">{entity.description}</p>

                  {/* Attributes */}
                  <div>
                    <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1">
                      Attributes / Columns
                    </span>
                    <ul className="space-y-1 bg-muted/40 p-2 rounded border border-border/40 text-xs font-mono">
                      {entity.attributes.map((attr, aIdx) => (
                        <li key={aIdx} className="text-muted-foreground flex items-center">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary/60 mr-2" />
                          {attr}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Foreign Keys if any */}
                  {entity.foreign_keys && entity.foreign_keys.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1">
                        Foreign Keys
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {entity.foreign_keys.map((fk, fIdx) => (
                          <Badge key={fIdx} variant="secondary" className="text-[10px]">
                            {fk}
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

        {/* Section 3: Relationships */}
        <AccordionItem value="relationships">
          <AccordionTrigger className="text-lg font-medium">Relationships ({database.relationships.length})</AccordionTrigger>
          <AccordionContent>
            <div className="bg-muted/30 p-4 rounded-lg border border-border">
              <ul className="space-y-2 text-sm">
                {database.relationships.map((rel, idx) => (
                  <li key={idx} className="flex items-center text-muted-foreground">
                    <span className="text-primary font-bold mr-3">🔗</span>
                    {rel}
                  </li>
                ))}
              </ul>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Section 4: ER Diagram */}
        <AccordionItem value="diagram">
          <AccordionTrigger className="text-lg font-medium">ER Diagram</AccordionTrigger>
          <AccordionContent>
            <MermaidDiagram chart={database.mermaid_er_diagram} />
          </AccordionContent>
        </AccordionItem>

        {/* Section 5: SQL Schema */}
        <AccordionItem value="sql">
          <AccordionTrigger className="text-lg font-medium flex items-center">
            SQL Schema (SQLite)
          </AccordionTrigger>
          <AccordionContent>
            <pre className="overflow-x-auto rounded-lg border border-border bg-muted/40 p-4 text-xs font-mono leading-relaxed text-foreground">
              <code>{database.sql_schema}</code>
            </pre>
          </AccordionContent>
        </AccordionItem>

      </Accordion>
    </div>
  );
};
