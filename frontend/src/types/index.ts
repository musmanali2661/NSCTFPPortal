export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface Student {
  id: number;
  reg_no: string;
  full_name: string;
  father_name: string;
  cnic: string;
  department: string;
  batch_type: string;
  status: string;
}

export interface StudentListResponse {
  items: Student[];
  total: number;
  page: number;
  size: number;
}

export interface DashboardStats {
  total_students: number;
  validated: number;
  pending_review: number;
  bulk_uploaded: number;
  student_registered: number;
  total_discrepancies: number;
  critical: number;
  high: number;
  resolved: number;
  students_per_department: { department: string; count: number }[];
}

export interface Discrepancy {
  id: number;
  student_reg_no: string;
  student_name: string;
  field_name: string;
  error_type: string;
  severity: string;
  is_resolved: boolean;
}

export interface DiscrepancyListResponse {
  items: Discrepancy[];
  total: number;
  page: number;
  size: number;
}

export interface UploadResult {
  created: number;
  updated: number;
  errors: number;
  row_errors: { row: number; message: string }[];
}

export interface Ticket {
  id: number;
  category: string;
  student_cnic: string;
  query: string;
  ai_reply: string | null;
  status: string;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  size: number;
}

export interface Question {
  id: number;
  subject_area: string;
  teacher: string;
  question_text: string;
  review_status: string;
}

export interface QuestionListResponse {
  items: Question[];
  total: number;
  page: number;
  size: number;
}
