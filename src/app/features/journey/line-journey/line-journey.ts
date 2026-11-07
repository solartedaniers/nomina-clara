import { Component, computed, inject } from '@angular/core';
import { PHASE_DEFINITIONS } from '../../../core/data/phase-definitions';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { CompileResponse, PhaseDefinition, PhaseStatus, TacInstructionDto, TokenDto } from '../../../core/models/compile.models';
import { WorkspaceStore } from '../../../core/services/workspace.store';
import { AstNode, astChildren, formatMoney, isAstNode, kindKey, nodeText, nodesOnLine } from '../../../shared/ast/ast';
import { Icon } from '../../../shared/icon/icon';
import { highlightLine, syntaxClass } from '../../../shared/syntax/syntax';

// Lo que muestra cada tarjeta del viaje: entrada, proceso y salida de la línea en esa fase
interface JourneyStep {
  definition: PhaseDefinition;
  status: PhaseStatus | null;
  input: string;
  process: string;
  output: string[];
  tokens: TokenDto[];
  // true cuando los datos de la fase no traen línea y se muestra un resumen de toda la fase
  summary: boolean;
  error: string | null;
}

const SUMMARY_LINES = 4;

@Component({
  selector: 'app-line-journey',
  imports: [TranslatePipe, Icon],
  template: `
    <section class="card">
      <header class="card-header">
        <div class="card-title">
          <span class="card-icon"><app-icon name="route" /></span>
          <div>
            <h2>{{ (line() ? 'journey.title' : 'journey.titleEmpty') | t: { line: line() ?? '' } }}</h2>
            <p>{{ 'journey.subtitle' | t }}</p>
          </div>
        </div>
        @if (line()) {
          <code class="source-line">@for (piece of sourcePieces(); track $index) {<span [class]="piece.cls">{{ piece.text }}</span>}</code>
        }
      </header>

      @if (!line()) {
        <p class="empty-state">
          <span class="empty-icon"><app-icon name="cursor" [size]="22" /></span>
          <span><strong>{{ 'journey.empty.title' | t }}</strong>{{ 'journey.empty.text' | t }}</span>
        </p>
      } @else {
        <div class="steps">
          @for (step of steps(); track step.definition.key) {
            <article [class]="'step phase-' + step.definition.key + ' state-' + (step.status ?? 'idle')">
              <header>
                <span class="phase-number">{{ step.definition.number }}</span>
                <b>{{ step.definition.labelKey | t }}</b>
              </header>
              @switch (step.status) {
                @case ('passed') {
                  <dl>
                    <dt>{{ 'journey.input' | t }}</dt>
                    <dd>{{ step.input }}</dd>
                    <dt>{{ 'journey.process' | t }}</dt>
                    <dd>{{ step.process }}</dd>
                    <dt>
                      {{ 'journey.output' | t }}
                      @if (step.summary) {
                        <span class="summary-tag">{{ 'journey.summaryTag' | t }}</span>
                      }
                    </dt>
                    <dd>
                      @for (token of step.tokens; track $index) {
                        <span [class]="'token-chip ' + classOf(token.type)" [title]="token.type">{{ token.value || '∅' }}</span>
                      }
                      @if (step.output.length) {
                        <pre class="mini">{{ step.output.join('\\n') }}</pre>
                      }
                    </dd>
                  </dl>
                }
                @case ('failed') {
                  <p class="state-message failed">
                    <app-icon name="alert" [size]="20" />
                    {{ step.error ?? ('status.failed' | t) }}
                  </p>
                }
                @default {
                  <p class="state-message">
                    <app-icon [name]="step.status === 'pending' ? 'hourglass' : 'route'" [size]="20" />
                    <strong>{{ 'status.' + (step.status ?? 'idle') | t }}</strong>
                    {{ step.definition.weekKey | t }}
                  </p>
                }
              }
            </article>
          }
        </div>
      }
    </section>
  `,
  styles: `
    .source-line {
      max-width: 55%;
      overflow: hidden;
      padding: 5px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #f3f6fa;
      font: 13px var(--mono);
      font-variant-ligatures: none;
      white-space: pre;
      text-overflow: ellipsis;
    }
    .steps {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 10px;
    }
    .step {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid var(--border);
      border-top: 4px solid var(--phase-color);
      border-radius: 12px;
      background: var(--surface);
    }
    .step > header {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 8px 10px 4px;
      font-size: 12.5px;
    }
    .step .phase-number {
      width: 22px;
      height: 22px;
      font-size: 12px;
    }
    dl {
      margin: 0;
      padding: 0 10px 10px;
      font-size: 11.5px;
    }
    dt {
      margin-top: 6px;
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--text-muted);
    }
    dd {
      margin: 2px 0 0;
      overflow-wrap: anywhere;
    }
    .token-chip {
      margin: 0 3px 3px 0;
      padding: 1px 5px;
      font-size: 10.5px;
    }
    .mini {
      margin: 0;
      padding: 4px 6px;
      overflow-x: auto;
      border-radius: 6px;
      background: var(--surface-muted);
      font: 10.5px/1.5 var(--mono);
      font-variant-ligatures: none;
      white-space: pre-wrap;
    }
    .summary-tag {
      margin-left: 4px;
      padding: 0 5px;
      border-radius: 5px;
      background: var(--brand-soft);
      color: var(--brand);
      letter-spacing: 0;
      text-transform: none;
    }
    .state-message {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      margin: auto 10px 14px;
      padding-top: 10px;
      text-align: center;
      font-size: 11.5px;
      color: var(--text-muted);
    }
    .state-message.failed {
      color: var(--danger);
    }
    .state-pending {
      border-style: dashed;
      border-top-style: solid;
      background: repeating-linear-gradient(135deg, #fffdf6, #fffdf6 8px, #fff9e8 8px, #fff9e8 16px);
    }
    .state-pending .state-message {
      color: #92400e;
    }
    .state-skipped,
    .state-idle {
      opacity: 0.6;
    }
    .state-failed {
      background: var(--danger-soft);
    }
    @media (max-width: 1100px) {
      .steps {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
  `,
})
export class LineJourney {
  protected readonly store = inject(WorkspaceStore);
  private readonly i18n = inject(I18nService);
  protected readonly classOf = syntaxClass;

  protected readonly line = this.store.selectedLine;

  protected readonly sourcePieces = computed(() => {
    const text = this.store.source().split('\n')[(this.line() ?? 1) - 1] ?? '';
    return highlightLine(text.trim());
  });

  protected readonly steps = computed<JourneyStep[]>(() => {
    const line = this.line();
    const response = this.store.response();
    return PHASE_DEFINITIONS.map((definition) => {
      const status = response?.status[definition.key] ?? null;
      const step: JourneyStep = { definition, status, input: '', process: '', output: [], tokens: [], summary: false, error: null };
      if (status === 'failed') {
        const error = this.store.errorFor(definition.key);
        step.error = error ? `${error.message}${error.line ? ` (${this.t('editor.line', { line: error.line })})` : ''}` : null;
      } else if (status === 'passed' && response && line) {
        this.describe(step, response, line);
      }
      return step;
    });
  });

  private t(key: string, params?: Record<string, string | number>): string {
    return this.i18n.translate(key, params);
  }

  private describe(step: JourneyStep, response: CompileResponse, line: number): void {
    const phases = response.phases;
    const key = step.definition.key;
    step.process = this.t(`journey.${key}.process`);
    const lineTokens = (phases.tokens ?? []).filter((token) => token.line === line && token.type !== 'EOF');

    switch (key) {
      case 'lexer':
        step.input = this.t('journey.lexer.input', { line });
        step.tokens = lineTokens;
        if (!lineTokens.length) {
          step.output = [this.t('journey.lexer.none')];
        }
        break;
      case 'parser': {
        step.input = this.t('journey.parser.input', { count: lineTokens.length });
        const ast = phases.ast;
        const nodes = isAstNode(ast) ? nodesOnLine(ast, line) : [];
        step.output = nodes.length ? nodes.flatMap((node) => this.treeLines(node, line)) : [this.t('journey.parser.none')];
        break;
      }
      case 'semantic': {
        step.input = this.t('journey.semantic.input');
        const symbols = phases.symbols ?? [];
        const own = symbols.filter((symbol) => symbol.line === line);
        step.summary = !own.length;
        step.output = (own.length ? own : symbols.slice(0, SUMMARY_LINES)).map(
          (symbol) => `${symbol.name}: ${symbol.type} · ${symbol.scope}`,
        );
        if (step.summary) {
          step.output.unshift(this.t('journey.semantic.summary', { count: symbols.length }));
        }
        break;
      }
      case 'ir':
        step.input = this.t('journey.ir.input');
        this.tacOutput(step, phases.tac?.tac ?? [], phases.tac?.text ?? [], line);
        break;
      case 'memory': {
        step.input = this.t('journey.memory.input');
        const memory = phases.memory;
        step.summary = true;
        step.output = [
          this.t('journey.memory.summary', {
            data: memory?.data.length ?? 0,
            stack: memory?.stack.length ?? 0,
            heap: memory?.heap.length ?? 0,
          }),
        ];
        break;
      }
      case 'optimizer': {
        step.input = this.t('journey.optimizer.input');
        const optimized = phases.optimized;
        this.tacOutput(step, optimized?.tac ?? [], optimized?.text ?? [], line);
        if (step.summary && optimized) {
          step.output[0] = this.t('journey.optimizer.summary', { before: optimized.originalCount, after: optimized.optimizedCount });
        }
        break;
      }
      case 'codegen': {
        step.input = this.t('journey.codegen.input');
        const assembly = phases.assembly;
        step.summary = true;
        step.output = [
          this.t('journey.codegen.summary', { count: assembly?.lines.length ?? 0, spills: assembly?.spills.length ?? 0 }),
          ...(assembly?.lines.slice(0, SUMMARY_LINES) ?? []),
        ];
        break;
      }
    }
  }

  // Instrucciones TAC de la línea si traen "line"; si no, un resumen con las primeras instrucciones
  private tacOutput(step: JourneyStep, tac: TacInstructionDto[], text: string[], line: number): void {
    const own = text.filter((_, index) => tac[index]?.line === line);
    if (own.length) {
      step.output = own;
      return;
    }
    step.summary = !tac.some((instruction) => typeof instruction.line === 'number');
    step.output = step.summary
      ? [this.t('journey.ir.summary', { count: text.length }), ...text.slice(0, SUMMARY_LINES)]
      : [this.t('journey.ir.none')];
  }

  // Mini árbol en texto de los nodos de la línea (solo los hijos de esa misma línea)
  private treeLines(node: AstNode, line: number, prefix = '', last = true, root = true): string[] {
    const evaluated = node.kind === 'ConstantDeclaration' && node['evaluated'] != null ? ` = ${formatMoney(node['evaluated'])}` : '';
    const label = `${this.t(kindKey(node))} ${nodeText(node)}`.trim();
    const own = root ? label : `${prefix}${last ? '└ ' : '├ '}${label}`;
    const children = astChildren(node).filter((child) => child.node.line === line);
    const childPrefix = root ? '' : prefix + (last ? '  ' : '│ ');
    // El valor de la constante va en su propia línea para que la tarjeta no quede tan ancha
    return [
      own,
      ...(evaluated ? [`${childPrefix}${evaluated.trim()}`] : []),
      ...children.flatMap((child, index) => this.treeLines(child.node, line, childPrefix, index === children.length - 1, false)),
    ];
  }
}
