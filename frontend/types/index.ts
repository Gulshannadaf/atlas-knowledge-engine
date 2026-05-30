/**
 * Shared TypeScript types for Atlas frontend
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: DocumentStatus;
  error_message: string | null;
  chunk_count: number;
  metadata: Record<string, unknown>;
  created_at: string;
  processed_at: string | null;
}

export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  citations: Citation[];
  token_count: number | null;
  latency_ms: number | null;
  created_at: string;
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Citation {
  document_id: string;
  document_name: string;
  chunk_id: string;
  content: string;
  relevance_score: number;
  page?: number;
  section?: string;
}

export interface Evaluation {
  id: string;
  name: string;
  description: string | null;
  status: EvaluationStatus;
  metrics: EvaluationMetrics;
  created_at: string;
  completed_at: string | null;
}

export type EvaluationStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface EvaluationMetrics {
  context_precision?: number;
  context_recall?: number;
  faithfulness?: number;
  answer_relevancy?: number;
  total_queries?: number;
  average_latency_ms?: number;
  average_cost_usd?: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  include_sources?: boolean;
  stream?: boolean;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  citations: Citation[];
  token_count: number | null;
  latency_ms: number | null;
  metadata: Record<string, unknown>;
}

export interface ApiError {
  detail: string;
  code?: string;
}
