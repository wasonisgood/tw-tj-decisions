export interface Metadata {
  case_no: string | null;
  applicant: string | null;
  subject: string | null;
  date: string | null;
}

export interface Content {
  full_text?: string;
  main_text?: string;
  facts?: string;
  reasoning?: string;
}

export interface StructuredReasoning {
  text: string;
  level: number;
  content: string[];
  children: StructuredReasoning[];
}

export interface Decision {
  id: string;
  filename: string;
  metadata: Metadata;
  content: Content;
  structured_reasoning?: StructuredReasoning[];
  tables?: any[];
}

export interface DecisionIndexItem {
  id: string;
  filename: string;
  metadata: Metadata;
}

export interface Revocation {
  id: string;
  name: string;
  category: number;
  court: string | string[];
  case_id: string | string[];
  crime: string | string[];
  sentence: string | string[];
  linked_decision_id?: string;
}
