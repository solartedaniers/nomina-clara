// Utilidades para recorrer el AST que llega en JSON (el formato de ast_nodes.py)

export type AstNode = Record<string, unknown> & { kind: string; line?: number };

export interface AstChild {
  role: string;
  node: AstNode;
}

export function isAstNode(value: unknown): value is AstNode {
  return typeof value === 'object' && value !== null && typeof (value as AstNode).kind === 'string';
}

// Hijos de un nodo en el orden en que vienen en el JSON (constantes, funciones, bloque, etc.)
export function astChildren(node: AstNode): AstChild[] {
  const children: AstChild[] = [];
  for (const [role, value] of Object.entries(node)) {
    if (isAstNode(value)) {
      children.push({ role, node: value });
    } else if (Array.isArray(value)) {
      value.filter(isAstNode).forEach((item) => children.push({ role, node: item }));
    }
  }
  return children;
}

export function countNodes(node: AstNode): number {
  return astChildren(node).reduce((total, child) => total + countNodes(child.node), 1);
}

// Nodos más externos que empiezan en una línea (sus hijos de la misma línea van dentro de ellos)
export function nodesOnLine(node: AstNode, line: number): AstNode[] {
  if (node.line === line && node.kind !== 'Program') {
    return [node];
  }
  return astChildren(node).flatMap((child) => nodesOnLine(child.node, line));
}

export function containsLine(node: AstNode, line: number | null): boolean {
  return line !== null && (node.line === line || astChildren(node).some((child) => containsLine(child.node, line)));
}

export function hasLines(node: AstNode | undefined): boolean {
  return typeof node?.line === 'number';
}

export function formatMoney(value: unknown): string {
  return '$' + Number(value).toLocaleString('es-CO', { maximumFractionDigits: 2 });
}

// Clave de es.json con el nombre del nodo en español (los números dicen si son enteros o decimales)
export function kindKey(node: AstNode): string {
  return node.kind === 'NumberLiteral' ? `ast.kinds.NumberLiteral.${node['type']}` : `ast.kinds.${node.kind}`;
}

// Tipo declarado que se muestra junto al nombre del nodo
export function declaredType(node: AstNode): string {
  const type = node['returnType'] ?? (node.kind === 'NumberLiteral' ? null : node['type']);
  return typeof type === 'string' ? type : '';
}

// Texto principal del nodo: su nombre, su operador o su valor
export function nodeText(node: AstNode): string {
  switch (node.kind) {
    case 'MoneyLiteral':
      return formatMoney(node['value']);
    case 'NumberLiteral':
      return String(node['value']);
    case 'StringLiteral':
      return `"${node['value']}"`;
    case 'BinaryOperation':
    case 'Comparison':
      return String(node['operator']);
    case 'FunctionCall':
      return `${node['name']}()`;
    case 'IfStatement':
      return 'si';
    case 'ReturnStatement':
      return 'retornar';
    case 'PayStatement':
      return 'pagar';
    case 'EmployeeBlock':
      return 'para cada empleado';
    default:
      return typeof node['name'] === 'string' ? node['name'] : '';
  }
}

// Grupo de color del nodo en el árbol
export function nodeGroup(node: AstNode): string {
  switch (node.kind) {
    case 'Program':
      return 'program';
    case 'BinaryOperation':
    case 'Comparison':
      return 'operator';
    case 'NumberLiteral':
    case 'StringLiteral':
      return 'literal';
    case 'MoneyLiteral':
      return 'money';
    case 'Identifier':
      return 'identifier';
    case 'FunctionDeclaration':
    case 'FunctionCall':
      return 'function';
    default:
      return 'statement';
  }
}
