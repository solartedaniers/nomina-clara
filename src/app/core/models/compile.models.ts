export type PhaseKey =
  | 'lexer'
  | 'parser'
  | 'semantic'
  | 'ir'
  | 'memory'
  | 'optimizer'
  | 'codegen'
  | 'execution';

export type PhaseStatus = 'passed' | 'failed' | 'pending' | 'skipped';

export interface Employee {
  nombre: string;
  salario: number;
  extras: number;
}

export interface CompileRequest {
  source: string;
  employees: Employee[];
}

export interface TokenDto {
  type: string;
  value: string;
  line: number;
  col: number;
}

export interface SymbolDto {
  name: string;
  type: string;
  scope: string;
  address: string;
  kind: string;
  line: number;
}

export interface TacInstructionDto {
  op: string;
  arg1: string | null;
  arg2: string | null;
  res: string | null;
}

export interface TacDto {
  tac: TacInstructionDto[];
  text: string[];
}

export interface OptimizedDto extends TacDto {
  originalCount: number;
  optimizedCount: number;
  removed: number;
  steps: string[];
}

export interface SpillDto {
  variable: string;
  register: string;
  address: string;
}

export interface AssemblyDto {
  lines: string[];
  spills: SpillDto[];
  unsupported: string[];
}

export interface MemoryDto {
  data: { name: string; value: unknown }[];
  stack: { function: string; locals: Record<string, unknown> }[];
  heap: { address: string; [key: string]: unknown }[];
  events: Record<string, unknown>[];
}

export interface CompilePhases {
  tokens?: TokenDto[];
  ast?: Record<string, unknown>;
  symbols?: SymbolDto[];
  tac?: TacDto;
  memory?: MemoryDto;
  optimized?: OptimizedDto;
  assembly?: AssemblyDto;
}

export interface PayrollEntry {
  name: string;
  values: Record<string, number | string>;
  pay: number;
}

export interface CompileError {
  phase: string;
  message: string;
  line: number;
  col: number;
  pending?: boolean;
}

export interface CompileResponse {
  ok: boolean;
  status: Record<PhaseKey, PhaseStatus>;
  phases: CompilePhases;
  payroll: PayrollEntry[];
  errors: CompileError[];
}

export interface PhaseDefinition {
  key: Exclude<PhaseKey, 'execution'>;
  number: number;
  labelKey: string;
  titleKey: string;
  weekKey: string;
}
