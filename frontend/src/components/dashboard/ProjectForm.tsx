import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { useState } from "react";

interface ProjectFormProps {
  onGenerate: (name: string, description: string, techStack: string) => void;
  generating: boolean;
}

export function ProjectForm({ onGenerate, generating }: ProjectFormProps) {
  const [name, setName] = useState("Trailhead");
  const [description, setDescription] = useState(
    "A social hiking log where users track completed trails, share photos, and get AI-suggested routes based on their fitness level."
  );
  const [techStack, setTechStack] = useState("react-fastapi");

  const handleSubmit = () => {
    onGenerate(name, description, techStack);
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-lg">New Project</CardTitle>
        <CardDescription>
          Describe your idea. The agents will do the planning.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="name">Project Name</Label>
          <Input 
            id="name" 
            placeholder="e.g. Trailhead — a hiking log app" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="desc">Project Description</Label>
          <Textarea
            id="desc"
            rows={5}
            placeholder="A short paragraph about what you want to build…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="stack">Preferred Tech Stack</Label>
          <Select value={techStack} onValueChange={setTechStack}>
            <SelectTrigger id="stack">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="react-fastapi">React + FastAPI</SelectItem>
              <SelectItem value="mern">MERN</SelectItem>
              <SelectItem value="django">Django</SelectItem>
              <SelectItem value="spring-boot">Spring Boot</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button onClick={handleSubmit} disabled={generating} className="w-full" size="lg">
          <Sparkles className="mr-1.5 h-4 w-4" />
          {generating ? "Generating…" : "Generate Blueprint"}
        </Button>
      </CardContent>
    </Card>
  );
}
