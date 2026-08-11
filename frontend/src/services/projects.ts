import { supabase } from "@/lib/supabase";
import { ProjectContextInput } from "./database";
import { ScaffoldResponse } from "./scaffold";

export interface ProjectRecord {
  id: string;
  user_id: string;
  name: string;
  description: string;
  tech_stack: string;
  requirements: any;
  architecture: any;
  database_design: any;
  documentation: any;
  scaffold: ScaffoldResponse | null;
  created_at: string;
}

/**
 * Fetch all projects for a specific user ID
 */
export async function fetchProjects(userId: string): Promise<ProjectRecord[]> {
  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .eq("user_id", userId)
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching projects:", error);
    throw error;
  }
  return data as ProjectRecord[];
}

/**
 * Save or update a project record for a user
 */
export async function saveProject(
  userId: string,
  name: string,
  description: string,
  techStack: string,
  context: ProjectContextInput,
  scaffold: ScaffoldResponse | null = null,
  existingProjectId: string | null = null
): Promise<ProjectRecord> {
  const recordData = {
    user_id: userId,
    name,
    description,
    tech_stack: techStack,
    requirements: context.requirements,
    architecture: context.architecture,
    database_design: context.database,
    documentation: context.documentation,
    scaffold,
  };

  let query;
  if (existingProjectId) {
    query = supabase
      .from("projects")
      .update(recordData)
      .eq("id", existingProjectId)
      .select()
      .single();
  } else {
    query = supabase.from("projects").insert([recordData]).select().single();
  }

  const { data, error } = await query;
  if (error) {
    console.error("Error saving project:", error);
    throw error;
  }
  return data as ProjectRecord;
}

/**
 * Delete a project record
 */
export async function deleteProject(projectId: string): Promise<void> {
  const { error } = await supabase.from("projects").delete().eq("id", projectId);
  if (error) {
    console.error("Error deleting project:", error);
    throw error;
  }
}
