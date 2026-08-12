/**
 * projects.ts
 * ──────────────────────────────────────────────────────────────
 * Supabase client helpers for the normalized BluePrint schema.
 * Tables: projects, project_requirements, project_architecture,
 *         project_database_schema, project_documentation,
 *         project_scaffold_files, generation_events
 */

import { supabase } from "@/lib/supabase";
import { RequirementsResponse } from "./requirements";
import { ArchitectureResponse } from "./architecture";
import { DatabaseResponse, ProjectContextInput } from "./database";
import { DocumentationResponse } from "./documentation";
import { ScaffoldResponse } from "./scaffold";

// ─── Public aggregate type for the list view ─────────────────────────────────
export interface ProjectSummary {
  id: string;
  user_id: string;
  name: string;
  description: string;
  tech_stack: string;
  status: "draft" | "generating" | "completed" | "failed";
  total_files: number;
  agents_done: number;
  total_agents: number;
  created_at: string;
  updated_at: string;
}

// ─── Full project with all section data ──────────────────────────────────────
export interface FullProject extends ProjectSummary {
  requirements: RequirementsResponse | null;
  architecture: ArchitectureResponse | null;
  database_design: DatabaseResponse | null;
  documentation: DocumentationResponse | null;
  scaffold: ScaffoldResponse | null;
}

// ─── CRUD helpers ─────────────────────────────────────────────────────────────

/** List all project headers for a user (lightweight, no section data) */
export async function fetchProjects(userId: string): Promise<ProjectSummary[]> {
  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .eq("user_id", userId)
    .order("created_at", { ascending: false });
  if (error) throw error;
  return (data ?? []) as ProjectSummary[];
}

/** Fetch a single project with ALL its section data joined */
export async function fetchFullProject(projectId: string): Promise<FullProject | null> {
  const { data: proj, error } = await supabase
    .from("projects")
    .select("*")
    .eq("id", projectId)
    .single();
  if (error || !proj) return null;

  const [req, arch, db, doc, scaffoldFiles] = await Promise.all([
    supabase.from("project_requirements").select("*").eq("project_id", projectId).maybeSingle(),
    supabase.from("project_architecture").select("*").eq("project_id", projectId).maybeSingle(),
    supabase.from("project_database_schema").select("*").eq("project_id", projectId).maybeSingle(),
    supabase.from("project_documentation").select("*").eq("project_id", projectId).maybeSingle(),
    supabase.from("project_scaffold_files").select("*").eq("project_id", projectId),
  ]);

  // Reconstruct scaffold response from individual file rows
  const scaffoldData: ScaffoldResponse | null =
    scaffoldFiles.data && scaffoldFiles.data.length > 0
      ? {
          project_name: proj.name,
          tree_view: "",
          total_files: scaffoldFiles.data.length,
          generation_summary: "",
          files: scaffoldFiles.data.map((f: any) => ({
            path: f.file_path,
            content: f.content ?? "",
            language: f.language ?? "text",
            generated_by: f.generated_by ?? "scaffold",
          })),
        }
      : null;

  return {
    ...(proj as ProjectSummary),
    requirements: req.data ? mapRequirements(req.data) : null,
    architecture: arch.data ? mapArchitecture(arch.data) : null,
    database_design: db.data ? mapDatabase(db.data) : null,
    documentation: doc.data ? mapDocumentation(doc.data) : null,
    scaffold: scaffoldData,
  };
}

/** Create a new project record and return its id */
export async function createProject(
  userId: string,
  name: string,
  description: string,
  techStack: string
): Promise<string> {
  const { data, error } = await supabase
    .from("projects")
    .insert([{ user_id: userId, name, description, tech_stack: techStack, status: "draft" }])
    .select("id")
    .single();
  if (error) throw error;
  return data.id as string;
}

/** Update project status + agent completion counter */
export async function updateProjectStatus(
  projectId: string,
  status: ProjectSummary["status"],
  agentsDone?: number,
  totalFiles?: number
): Promise<void> {
  const patch: Record<string, any> = { status };
  if (agentsDone !== undefined) patch.agents_done = agentsDone;
  if (totalFiles !== undefined) patch.total_files = totalFiles;
  const { error } = await supabase.from("projects").update(patch).eq("id", projectId);
  if (error) throw error;
}

/** Upsert the requirements section */
export async function saveRequirements(projectId: string, req: RequirementsResponse): Promise<void> {
  const { error } = await supabase.from("project_requirements").upsert({
    project_id: projectId,
    project_name: req.project_name,
    project_overview: req.project_overview,
    objectives: req.objectives,
    functional_requirements: req.functional_requirements,
    non_functional_requirements: req.non_functional_requirements,
    user_roles: req.user_roles,
    assumptions: req.assumptions,
    constraints: req.constraints,
    future_scope: req.future_scope,
    suggested_modules: req.suggested_modules,
    user_stories: req.user_stories,
    recommended_tech_stack: req.recommended_tech_stack,
  }, { onConflict: "project_id" });
  if (error) throw error;
}

/** Upsert the architecture section */
export async function saveArchitecture(projectId: string, arch: ArchitectureResponse): Promise<void> {
  const { error } = await supabase.from("project_architecture").upsert({
    project_id: projectId,
    high_level_architecture: arch.high_level_architecture,
    data_flow: arch.data_flow,
    folder_structure: arch.folder_structure,
    component_breakdown: arch.component_breakdown,
  }, { onConflict: "project_id" });
  if (error) throw error;
}

/** Upsert the database schema section */
export async function saveDatabase(projectId: string, db: DatabaseResponse): Promise<void> {
  const { error } = await supabase.from("project_database_schema").upsert({
    project_id: projectId,
    database_overview: db.database_overview,
    normalization_notes: db.normalization_notes,
    table_summary: db.table_summary,
    relationships: db.relationships,
    sql_schema: db.sql_schema,
    mermaid_er_diagram: db.mermaid_er_diagram,
    entities: db.entities,
  }, { onConflict: "project_id" });
  if (error) throw error;
}

/** Upsert the documentation section */
export async function saveDocumentation(projectId: string, doc: DocumentationResponse): Promise<void> {
  const { error } = await supabase.from("project_documentation").upsert({
    project_id: projectId,
    project_overview: doc.project_overview,
    readme_md: doc.readme_md,
    installation_guide: doc.installation_guide,
    api_documentation: doc.api_documentation,
    folder_structure_description: doc.folder_structure_description,
    deployment_notes: doc.deployment_notes,
    developer_notes: doc.developer_notes,
  }, { onConflict: "project_id" });
  if (error) throw error;
}

/** Upsert all scaffold files (delete old, insert new) */
export async function saveScaffoldFiles(projectId: string, scaffold: ScaffoldResponse): Promise<void> {
  // Delete old files first
  await supabase.from("project_scaffold_files").delete().eq("project_id", projectId);
  if (!scaffold.files.length) return;
  
  const rows = scaffold.files.map((f) => ({
    project_id: projectId,
    file_path: f.path,
    content: f.content,
    language: f.language,
    generated_by: f.generated_by,
  }));
  const { error } = await supabase.from("project_scaffold_files").insert(rows);
  if (error) throw error;
}

/** Log a generation event for audit trail */
export async function logGenerationEvent(
  projectId: string,
  agentId: string,
  status: "started" | "completed" | "failed",
  durationMs?: number,
  errorMsg?: string
): Promise<void> {
  const { error } = await supabase.from("generation_events").insert({
    project_id: projectId,
    agent_id: agentId,
    status,
    duration_ms: durationMs ?? null,
    error_msg: errorMsg ?? null,
  });
  if (error) console.warn("Failed to log generation event:", error);
}

/** Delete a project (cascades to all child tables) */
export async function deleteProject(projectId: string): Promise<void> {
  const { error } = await supabase.from("projects").delete().eq("id", projectId);
  if (error) throw error;
}

// ─── Field mappers (DB row → frontend interface) ──────────────────────────────

function mapRequirements(row: any): RequirementsResponse {
  return {
    project_name: row.project_name,
    project_overview: row.project_overview,
    objectives: row.objectives ?? [],
    functional_requirements: row.functional_requirements ?? [],
    non_functional_requirements: row.non_functional_requirements ?? [],
    user_roles: row.user_roles ?? [],
    user_stories: row.user_stories ?? [],
    suggested_modules: row.suggested_modules ?? [],
    assumptions: row.assumptions ?? [],
    constraints: row.constraints ?? [],
    recommended_tech_stack: row.recommended_tech_stack ?? {},
    future_scope: row.future_scope ?? [],
  };
}

function mapArchitecture(row: any): ArchitectureResponse {
  return {
    high_level_architecture: row.high_level_architecture,
    folder_structure: row.folder_structure ?? [],
    component_breakdown: row.component_breakdown ?? [],
    data_flow: row.data_flow,
  };
}

function mapDatabase(row: any): DatabaseResponse {
  return {
    database_overview: row.database_overview,
    entities: row.entities ?? [],
    relationships: row.relationships ?? [],
    normalization_notes: row.normalization_notes,
    table_summary: row.table_summary,
    sql_schema: row.sql_schema,
    mermaid_er_diagram: row.mermaid_er_diagram,
  };
}

function mapDocumentation(row: any): DocumentationResponse {
  return {
    project_overview: row.project_overview,
    readme_md: row.readme_md,
    installation_guide: row.installation_guide,
    api_documentation: row.api_documentation,
    folder_structure_description: row.folder_structure_description,
    deployment_notes: row.deployment_notes,
    developer_notes: row.developer_notes,
  };
}
