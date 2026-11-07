// Resaltado de sintaxis del lenguaje Nómina Clara.
// Usa las mismas reglas y el mismo orden que TOKEN_SPECS en compiler/tokens.py,
// así el color del editor coincide con el token que va a producir el lexer.

const KEYWORDS = new Set(['constante', 'funcion', 'para', 'cada', 'empleado', 'si', 'sino', 'retornar', 'pagar']);
const DATA_TYPES = new Set(['entero', 'decimal', 'dinero', 'texto', 'logico']);

const PATTERNS: [string, RegExp][] = [
  ['COMMENT', /#[^\n]*/y],
  ['SKIP', /[ \t\r]+/y],
  ['MONEY', /\$(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?![0-9.])/y],
  ['DECIMAL', /[0-9]+\.[0-9]+/y],
  ['INTEGER', /[0-9]+/y],
  ['STRING', /"[^"\n]*"/y],
  ['IDENTIFIER', /[a-zA-Z_][a-zA-Z0-9_]*/y],
  ['REL_OP', /<=|>=|==|!=|<|>/y],
  ['ARITH_OP', /[+\-*/]/y],
  ['ASSIGN', /=/y],
  ['PUNCT', /[:,(){}]/y],
];

// Clase CSS (definida en styles.css) para cada tipo de token
const CLASSES: Record<string, string> = {
  KEYWORD: 'syn-keyword',
  TYPE: 'syn-type',
  MONEY: 'syn-money',
  DECIMAL: 'syn-number',
  INTEGER: 'syn-number',
  STRING: 'syn-string',
  IDENTIFIER: 'syn-identifier',
  REL_OP: 'syn-operator',
  ARITH_OP: 'syn-operator',
  ASSIGN: 'syn-operator',
  COMMENT: 'syn-comment',
  INVALID: 'syn-invalid',
};

export function syntaxClass(tokenType: string): string {
  return CLASSES[tokenType] ?? 'syn-punct';
}

export interface SyntaxPiece {
  text: string;
  cls: string;
}

export function highlightLine(line: string): SyntaxPiece[] {
  const pieces: SyntaxPiece[] = [];
  let pos = 0;
  while (pos < line.length) {
    let kind = 'INVALID';
    let text = line[pos];
    for (const [name, pattern] of PATTERNS) {
      pattern.lastIndex = pos;
      const match = pattern.exec(line);
      if (match) {
        kind = name;
        text = match[0];
        break;
      }
    }
    if (kind === 'IDENTIFIER' && KEYWORDS.has(text)) {
      kind = 'KEYWORD';
    } else if (kind === 'IDENTIFIER' && DATA_TYPES.has(text)) {
      kind = 'TYPE';
    }
    pieces.push({ text, cls: kind === 'SKIP' ? '' : syntaxClass(kind) });
    pos += text.length;
  }
  return pieces;
}
