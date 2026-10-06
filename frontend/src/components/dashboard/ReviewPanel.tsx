import React, { useState } from "react";
import { ProjectContextInput } from "@/services/database";
import { critiqueBlueprint, ReviewResponse } from "@/services/review";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle, ShieldAlert, Zap } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ReviewPanelProps {
  context: ProjectContextInput;
}

export const ReviewPanel: React.FC<ReviewPanelProps> = ({ context }) => {
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { architecture, database } = context;
  const isReady = architecture !== null && database !== null;

  const handleCritique = async () => {
    if (!isReady) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const result = await critiqueBlueprint({
        architecture: architecture!,
        database: database!
      });
      setReview(result);
    } catch (err: any) {
      console.error("Failed to run critique:", err);
      setError(err.response?.data?.detail || err.message || "Critique failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isReady) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Blueprint Incomplete</h3>
        <p className="text-muted-foreground max-w-md mt-2">
          Please generate both Architecture and Database first before running the AI Critique.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <h3 className="text-lg font-medium">Architecture Review Board is active</h3>
        <p className="text-muted-foreground animate-pulse text-sm">
          The Senior Security Expert and DevOps Engineer are debating your blueprint... this may take a few minutes.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="my-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Review Failed</AlertTitle>
        <AlertDescription className="mt-2">
          {error}
          <div className="mt-4">
            <Button variant="outline" size="sm" onClick={handleCritique}>
              Retry Critique
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!review) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center border rounded-lg border-dashed bg-muted/20">
        <ShieldAlert className="w-12 h-12 text-primary mb-4" />
        <h3 className="text-lg font-medium text-foreground mb-2">Architecture Review Board</h3>
        <p className="text-muted-foreground max-w-md mb-6">
          Deploy an autonomous AI team consisting of a Security Expert and a DevOps Engineer to critique your Architecture and Database design.
        </p>
        <Button onClick={handleCritique} size="lg" className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2">
          <Zap className="w-4 h-4" /> Run AI Critique
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-indigo-500" />
            Risk & Recommendations Report
          </h2>
          <p className="text-muted-foreground">Findings from the Security and DevOps experts.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleCritique} className="gap-2">
          <Zap className="w-4 h-4" /> Re-run Critique
        </Button>
      </div>

      <div className="bg-indigo-50/50 border border-indigo-100 rounded-lg p-4">
        <h3 className="font-semibold text-indigo-900 mb-2">Executive Summary</h3>
        <p className="text-sm text-indigo-800 leading-relaxed">{review.summary}</p>
      </div>

      <div className="space-y-4 mt-6">
        <h3 className="text-lg font-medium">Identified Risks</h3>
        {review.recommendations.map((rec, idx) => (
          <div key={idx} className="bg-card border border-border shadow-sm rounded-lg p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full ${
                rec.category.toLowerCase().includes('security') 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-orange-100 text-orange-700'
              }`}>
                {rec.category}
              </span>
            </div>
            <p className="font-semibold text-foreground text-sm mt-1">{rec.issue}</p>
            <div className="bg-muted/40 p-3 rounded mt-2 border border-border/50">
              <p className="text-sm text-muted-foreground"><span className="font-semibold text-foreground">Recommendation:</span> {rec.suggestion}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
