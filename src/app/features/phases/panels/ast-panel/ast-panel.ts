import { NgTemplateOutlet } from '@angular/common';
import { Component, ElementRef, afterRenderEffect, computed, inject, input, linkedSignal, signal, viewChild } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../../core/services/workspace.store';
import {
  AstNode,
  astChildren,
  containsLine,
  countNodes,
  declaredType,
  formatMoney,
  isAstNode,
  kindKey,
  nodeGroup,
  nodeText,
} from '../../../../shared/ast/ast';
import { Icon } from '../../../../shared/icon/icon';
import { JsonView } from '../../../../shared/json-view/json-view';

// Nodo ya preparado para dibujar, así el template no recalcula nada
interface TreeNode {
  id: string;
  depth: number;
  role: string;
  line: number | null;
  kindKey: string;
  type: string;
  text: string;
  group: string;
  evaluated: string | null;
  hidden: number;
  source: AstNode;
  children: TreeNode[];
}

// Partes del "si" que llevan un rótulo encima (condición, entonces, sino)
const ROLES = new Set(['condition', 'then', 'else']);

function buildTree(node: AstNode, id = 'n', depth = 0, role = ''): TreeNode {
  const evaluated = node.kind === 'ConstantDeclaration' && node['evaluated'] != null ? formatMoney(node['evaluated']) : null;
  return {
    id,
    depth,
    role: ROLES.has(role) ? role : '',
    // El programa no tiene una línea propia: el nodo raíz solo dice "Programa"
    line: typeof node.line === 'number' && node.kind !== 'Program' ? node.line : null,
    kindKey: kindKey(node),
    type: declaredType(node),
    text: nodeText(node),
    group: nodeGroup(node),
    evaluated,
    hidden: countNodes(node) - 1,
    source: node,
    children: astChildren(node).map((child, index) => buildTree(child.node, `${id}.${index}`, depth + 1, child.role)),
  };
}

// Panel de la fase 2 · Responsable: Daniers
// Dibuja el AST como árbol con nodos y líneas (CSS), con la opción de ver el JSON
@Component({
  selector: 'app-ast-panel',
  imports: [TranslatePipe, JsonView, NgTemplateOutlet, Icon],
  template: `
    @if (tree(); as root) {
      <div class="toolbar">
        <div class="segmented">
          <button type="button" [class.active]="view() === 'tree'" (click)="view.set('tree')">{{ 'ast.tree' | t }}</button>
          <button type="button" [class.active]="view() === 'json'" (click)="view.set('json')">JSON</button>
        </div>
        @if (view() === 'tree') {
          <span class="hint">{{ 'ast.hint' | t }}</span>
          <div class="zoom">
            <button type="button" (click)="zoomBy(-0.1)" [attr.aria-label]="'ast.zoomOut' | t"><app-icon name="minus" [size]="14" /></button>
            <span>{{ zoomLabel() }}</span>
            <button type="button" (click)="zoomBy(0.1)" [attr.aria-label]="'ast.zoomIn' | t"><app-icon name="plus" [size]="14" /></button>
          </div>
        }
      </div>
      @if (view() === 'tree') {
        <div class="tree-wrap" #treeWrap>
          <ul class="tree" [style.zoom]="zoom()">
            <ng-container *ngTemplateOutlet="branch; context: { $implicit: root }" />
          </ul>
        </div>
      } @else {
        <app-json-view [value]="ast()" />
      }
    }

    <ng-template #branch let-node>
      <li>
        @if (node.role) {
          <span class="role">{{ 'ast.roles.' + node.role | t }}</span>
        }
        <button
          type="button"
          [class]="'node group-' + node.group"
          [class.on-line]="node.line !== null && node.line === store.selectedLine()"
          [class.closed]="node.children.length && !isOpen(node)"
          (click)="toggle(node)"
        >
          @if (node.line !== null) {
            <span class="line-badge">L{{ node.line }}</span>
          }
          <small>{{ node.kindKey | t }}@if (node.type) { · {{ node.type }}}</small>
          @if (node.text) {
            <b>{{ node.text }}</b>
          }
          @if (node.evaluated) {
            <span class="evaluated">= {{ node.evaluated }}</span>
          }
        </button>
        @if (node.children.length) {
          <ul>
            @if (isOpen(node)) {
              @for (child of node.children; track child.id) {
                <ng-container *ngTemplateOutlet="branch; context: { $implicit: child }" />
              }
            } @else {
              <li><button type="button" class="node more" (click)="toggle(node)">{{ (node.hidden === 1 ? 'ast.moreOne' : 'ast.more') | t: { count: node.hidden } }}</button></li>
            }
          </ul>
        }
      </li>
    </ng-template>
  `,
  styles: `
    :host {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 300px;
    }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
    }
    .toolbar .hint {
      flex: 1;
    }
    .segmented,
    .zoom {
      display: flex;
      align-items: center;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      font-size: 12px;
    }
    .segmented button,
    .zoom button {
      display: grid;
      place-items: center;
      border: 0;
      padding: 5px 10px;
      background: var(--surface);
      color: var(--text-muted);
      font: 600 12px 'Inter', sans-serif;
      cursor: pointer;
    }
    .segmented button.active {
      background: var(--brand);
      color: #fff;
    }
    .zoom span {
      min-width: 40px;
      text-align: center;
      color: var(--text-muted);
    }
    .tree-wrap {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 12px 8px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: radial-gradient(#e6ebf3 1px, transparent 1px) 0 0 / 16px 16px;
    }
  `,
})
export class AstPanel {
  readonly ast = input<Record<string, unknown> | undefined>(undefined);
  protected readonly store = inject(WorkspaceStore);

  protected readonly view = signal<'tree' | 'json'>('tree');
  protected readonly zoom = signal(1);
  protected readonly zoomLabel = computed(() => `${Math.round(this.zoom() * 100)}%`);
  protected readonly tree = computed(() => {
    const ast = this.ast();
    return isAstNode(ast) ? buildTree(ast) : null;
  });

  // Nodos que el usuario abrió o cerró a mano; se reinicia con cada AST nuevo
  private readonly toggled = linkedSignal(() => {
    this.tree();
    return new Map<string, boolean>();
  });

  private readonly treeWrap = viewChild<ElementRef<HTMLElement>>('treeWrap');

  constructor() {
    // Lleva a la vista el primer nodo de la línea seleccionada
    afterRenderEffect(() => {
      this.store.selectedLine();
      const node = this.treeWrap()?.nativeElement.querySelector('.on-line');
      node?.scrollIntoView({ block: 'nearest', inline: 'center' });
    });
  }

  // Por defecto se ven la raíz y sus hijos, y además las ramas que contienen la línea seleccionada
  protected isOpen(node: TreeNode): boolean {
    return this.toggled().get(node.id) ?? (node.depth < 1 || containsLine(node.source, this.store.selectedLine()));
  }

  protected toggle(node: TreeNode): void {
    if (!node.children.length) {
      if (node.line !== null) {
        this.store.selectedLine.set(node.line);
      }
      return;
    }
    const open = this.isOpen(node);
    this.toggled.update((map) => new Map(map).set(node.id, !open));
  }

  protected zoomBy(step: number): void {
    this.zoom.update((value) => Math.min(1.5, Math.max(0.5, Math.round((value + step) * 10) / 10)));
  }
}
