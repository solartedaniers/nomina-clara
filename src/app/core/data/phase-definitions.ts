import { PhaseDefinition } from '../models/compile.models';

export const PHASE_DEFINITIONS: PhaseDefinition[] = [
  { key: 'lexer', number: 1, labelKey: 'phases.lexer.label', titleKey: 'phases.lexer.title', weekKey: 'phases.lexer.week' },
  { key: 'parser', number: 2, labelKey: 'phases.parser.label', titleKey: 'phases.parser.title', weekKey: 'phases.parser.week' },
  { key: 'semantic', number: 3, labelKey: 'phases.semantic.label', titleKey: 'phases.semantic.title', weekKey: 'phases.semantic.week' },
  { key: 'ir', number: 4, labelKey: 'phases.ir.label', titleKey: 'phases.ir.title', weekKey: 'phases.ir.week' },
  { key: 'memory', number: 5, labelKey: 'phases.memory.label', titleKey: 'phases.memory.title', weekKey: 'phases.memory.week' },
  { key: 'optimizer', number: 6, labelKey: 'phases.optimizer.label', titleKey: 'phases.optimizer.title', weekKey: 'phases.optimizer.week' },
  { key: 'codegen', number: 7, labelKey: 'phases.codegen.label', titleKey: 'phases.codegen.title', weekKey: 'phases.codegen.week' },
];
