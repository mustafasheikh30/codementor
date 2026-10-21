// These mirror the FastAPI response schemas (app/problems/schemas.py).
// Field names stay snake_case so they match the JSON exactly.

export interface Problem {
  contest_id: number;
  index: string;
  name: string;
  rating: number | null;
  tags: string[];
  solved_count: number | null;
  url: string;
}

export interface ProblemPage {
  total: number;
  page: number;
  page_size: number;
  items: Problem[];
}

export interface TagCount {
  tag: string;
  count: number;
}

export interface Meta {
  problem_count: number;
  has_sample_data: boolean;
}

export interface ProblemQuery {
  q?: string;
  tag?: string;
  min_rating?: string;
  max_rating?: string;
  sort?: string;
  page?: number;
}
