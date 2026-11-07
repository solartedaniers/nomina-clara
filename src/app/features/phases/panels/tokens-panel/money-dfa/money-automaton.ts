// Autómata finito determinista (DFA) del token MONEY.
// Equivale al patrón de compiler/tokens.py:  \$(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?![0-9.])
//
//   q0 --$--> q1 --d--> q2 --d--> q3 --d--> q4 --d--> q5 (d: se queda en q5)
//                        \         |         /
//                         '--.--> q6 <--.---'          q9 --.--> q6
//                                 q6 --d--> q7 --d--> q8 --d--> q9
//
// Aceptación: q2, q3, q4 (1 a 3 dígitos), q5 (4 o más dígitos sin puntos) y q9 (grupo de 3 dígitos completo).
// El lookahead (?![0-9.]) del regex corresponde a que el valor termine en un estado de aceptación
// sin poder seguir: por ejemplo $1.7509 llega a q9 con "$1.750" y el "9" no tiene transición.

export type MoneyState = 'q0' | 'q1' | 'q2' | 'q3' | 'q4' | 'q5' | 'q6' | 'q7' | 'q8' | 'q9';
export type MoneySymbol = 'dollar' | 'digit' | 'dot';

export const MONEY_STATES: MoneyState[] = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9'];
export const MONEY_START: MoneyState = 'q0';
export const MONEY_ACCEPTING = new Set<MoneyState>(['q2', 'q3', 'q4', 'q5', 'q9']);

// Tabla de transiciones: estado -> símbolo -> estado siguiente (si no está, no hay transición)
export const MONEY_TRANSITIONS: Record<MoneyState, Partial<Record<MoneySymbol, MoneyState>>> = {
  q0: { dollar: 'q1' },
  q1: { digit: 'q2' },
  q2: { digit: 'q3', dot: 'q6' },
  q3: { digit: 'q4', dot: 'q6' },
  q4: { digit: 'q5', dot: 'q6' },
  q5: { digit: 'q5' },
  q6: { digit: 'q7' },
  q7: { digit: 'q8' },
  q8: { digit: 'q9' },
  q9: { dot: 'q6' },
};

export interface MoneyStep {
  from: MoneyState;
  to: MoneyState;
  char: string;
}

export interface MoneyTrace {
  steps: MoneyStep[];
  accepted: boolean;
  // Estado donde se detuvo y carácter que no tuvo transición (si lo hubo)
  last: MoneyState;
  stuckAt: string | null;
}

function symbolOf(char: string): MoneySymbol | null {
  if (char === '$') return 'dollar';
  if (char === '.') return 'dot';
  return char >= '0' && char <= '9' ? 'digit' : null;
}

// Recorre el valor carácter por carácter y guarda cada transición usada
export function traceMoney(value: string): MoneyTrace {
  const steps: MoneyStep[] = [];
  let state = MONEY_START;
  for (const char of value) {
    const symbol = symbolOf(char);
    const next = symbol ? MONEY_TRANSITIONS[state][symbol] : undefined;
    if (!next) {
      return { steps, accepted: false, last: state, stuckAt: char };
    }
    steps.push({ from: state, to: next, char });
    state = next;
  }
  return { steps, accepted: MONEY_ACCEPTING.has(state), last: state, stuckAt: null };
}
