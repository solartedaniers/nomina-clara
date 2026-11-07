import { Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../../core/i18n/translate.pipe';
import { MONEY_ACCEPTING, MONEY_PATTERN, MONEY_STATES, MoneyState, traceMoney } from './money-automaton';

const RADIUS = 20;
const ARROW = 5;

// Posición de cada estado en el dibujo: arriba la parte sin puntos, abajo los grupos de miles
const POSITIONS: Record<MoneyState, [number, number]> = {
  q0: [60, 70],
  q1: [150, 70],
  q2: [240, 70],
  q3: [330, 70],
  q4: [420, 70],
  q5: [510, 70],
  q6: [330, 200],
  q7: [420, 200],
  q8: [510, 200],
  q9: [600, 200],
};

interface Edge {
  key: string;
  label: string;
  path: string;
  labelX: number;
  labelY: number;
}

// Flecha recta entre dos estados, recortada en el borde de los círculos
function straight(from: MoneyState, to: MoneyState, label: string, side = 1): Edge {
  const [x1, y1] = POSITIONS[from];
  const [x2, y2] = POSITIONS[to];
  const length = Math.hypot(x2 - x1, y2 - y1);
  const [ux, uy] = [(x2 - x1) / length, (y2 - y1) / length];
  const start = [x1 + ux * RADIUS, y1 + uy * RADIUS];
  const end = [x2 - ux * (RADIUS + ARROW), y2 - uy * (RADIUS + ARROW)];
  return {
    key: `${from}>${to}`,
    label,
    path: `M ${start[0]} ${start[1]} L ${end[0]} ${end[1]}`,
    labelX: (x1 + x2) / 2 - uy * 11 * side,
    labelY: (y1 + y2) / 2 + ux * 11 * side * -1 + 4,
  };
}

const EDGES: Edge[] = [
  straight('q0', 'q1', '$'),
  straight('q1', 'q2', '0-9'),
  straight('q2', 'q3', '0-9'),
  straight('q3', 'q4', '0-9'),
  straight('q4', 'q5', '0-9'),
  straight('q2', 'q6', "'.'"),
  straight('q3', 'q6', "'.'", -1),
  straight('q4', 'q6', "'.'", -1),
  straight('q6', 'q7', '0-9'),
  straight('q7', 'q8', '0-9'),
  straight('q8', 'q9', '0-9'),
  // Bucle de q5 sobre sí mismo y regreso de q9 a q6 por debajo
  { key: 'q5>q5', label: '0-9', path: 'M 498 52 C 478 6, 542 6, 522 50', labelX: 548, labelY: 30 },
  { key: 'q9>q6', label: "'.'", path: 'M 592 219 C 560 275, 380 275, 340 223', labelX: 465, labelY: 282 },
];

// Panel de la fase 1 · Responsable: Daniers
// Dibuja el DFA del token MONEY y resalta el recorrido del valor elegido
@Component({
  selector: 'app-money-dfa',
  imports: [TranslatePipe],
  template: `
    <section class="dfa">
      <header>
        <h3>{{ 'moneyDfa.title' | t }}</h3>
        <code>{{ pattern }}</code>
      </header>
      <svg viewBox="0 0 660 290" role="img" [attr.aria-label]="'moneyDfa.title' | t">
        <defs>
          <marker id="dfa-arrow" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
          </marker>
          <marker id="dfa-arrow-active" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#15803d" />
          </marker>
        </defs>

        <!-- Flecha de inicio hacia q0 -->
        <path d="M 8 70 L 35 70" class="edge" [class.active]="value()" marker-end="url(#dfa-arrow)" />

        @for (edge of edges; track edge.key) {
          @let active = usedEdges().has(edge.key);
          <path [attr.d]="edge.path" class="edge" [class.active]="active"
            [attr.marker-end]="active ? 'url(#dfa-arrow-active)' : 'url(#dfa-arrow)'" />
          <text [attr.x]="edge.labelX" [attr.y]="edge.labelY" class="edge-label" [class.active]="active">{{ edge.label }}</text>
        }

        @for (state of states; track state) {
          @let x = positions[state][0];
          @let y = positions[state][1];
          <g [class]="'state ' + stateClass(state)">
            <title>{{ state }}: {{ 'moneyDfa.states.' + state | t }}</title>
            <circle [attr.cx]="x" [attr.cy]="y" [attr.r]="radius" />
            @if (accepting.has(state)) {
              <circle [attr.cx]="x" [attr.cy]="y" [attr.r]="radius - 4" class="inner" />
            }
            <text [attr.x]="x" [attr.y]="y + 4">{{ state }}</text>
          </g>
        }
      </svg>

      <p class="legend">
        <span><i class="ring"></i>{{ 'moneyDfa.legend.state' | t }}</span>
        <span><i class="ring double"></i>{{ 'moneyDfa.legend.accepting' | t }}</span>
        <span><i class="ring visited"></i>{{ 'moneyDfa.legend.path' | t }}</span>
      </p>

      @if (trace(); as trace) {
        <div class="path" [class.rejected]="!trace.accepted">
          <strong>{{ value() }}</strong>
          <span class="steps">
            <span class="step-state">q0</span>
            @for (step of trace.steps; track $index) {
              <span class="step-char">{{ step.char }}</span><span class="step-state">{{ step.to }}</span>
            }
          </span>
          <span class="verdict">
            @if (trace.accepted) {
              {{ 'moneyDfa.accepted' | t: { state: trace.last } }}
            } @else if (trace.stuckAt) {
              {{ 'moneyDfa.stuck' | t: { state: trace.last, char: trace.stuckAt } }}
            } @else {
              {{ 'moneyDfa.notAccepting' | t: { state: trace.last } }}
            }
          </span>
        </div>
      } @else {
        <p class="hint">{{ 'moneyDfa.hint' | t }}</p>
      }
    </section>
  `,
  styles: `
    .dfa {
      margin-top: 14px;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 10px;
    }
    header {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 6px 12px;
    }
    h3 {
      margin: 0;
    }
    code {
      font: 11px var(--mono);
      font-variant-ligatures: none;
      color: var(--text-muted);
    }
    svg {
      display: block;
      width: 100%;
      max-width: 660px;
      margin: 4px auto 0;
      font-family: var(--mono);
    }
    .edge {
      fill: none;
      stroke: #94a3b8;
      stroke-width: 1.6;
    }
    .edge.active {
      stroke: #15803d;
      stroke-width: 2.6;
    }
    .edge-label {
      font-size: 12px;
      text-anchor: middle;
      fill: var(--text-muted);
    }
    .edge-label.active {
      fill: #15803d;
      font-weight: 700;
    }
    .state circle {
      fill: var(--surface);
      stroke: var(--brand);
      stroke-width: 1.6;
    }
    .state text {
      font-size: 12px;
      font-weight: 600;
      text-anchor: middle;
      fill: var(--text);
    }
    .state.visited circle {
      fill: #ecfdf3;
      stroke: #15803d;
      stroke-width: 2.2;
    }
    .state.final-ok circle {
      fill: #15803d;
      stroke: #15803d;
    }
    .state.final-ok text,
    .state.final-bad text {
      fill: #fff;
    }
    .state.final-ok .inner {
      stroke: #fff;
    }
    .state.final-bad circle {
      fill: var(--danger);
      stroke: var(--danger);
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin: 4px 0 0;
      font-size: 11.5px;
      color: var(--text-muted);
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .ring {
      width: 12px;
      height: 12px;
      border: 1.6px solid var(--brand);
      border-radius: 50%;
    }
    .ring.double {
      outline: 1.6px solid var(--brand);
      outline-offset: 1.5px;
      width: 8px;
      height: 8px;
      margin: 2px;
    }
    .ring.visited {
      border-color: #15803d;
      background: #ecfdf3;
    }
    .path {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px 12px;
      margin-top: 10px;
      padding: 8px 10px;
      border-radius: 8px;
      background: var(--success-soft);
      font-size: 12px;
    }
    .path.rejected {
      background: var(--danger-soft);
    }
    .path strong {
      font: 600 13px var(--mono);
      color: #15803d;
    }
    .steps {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 3px;
      font: 11.5px var(--mono);
    }
    .step-state {
      padding: 1px 5px;
      border-radius: 5px;
      background: var(--surface);
      border: 1px solid #a7d7b8;
    }
    .step-char::before {
      content: '—';
      color: var(--text-muted);
    }
    .step-char::after {
      content: '→';
      color: var(--text-muted);
    }
    .step-char {
      font-weight: 700;
      color: #15803d;
    }
    .verdict {
      color: var(--text-muted);
    }
    .hint {
      margin: 8px 0 0;
    }
  `,
})
export class MoneyDfa {
  readonly value = input<string | null>(null);

  protected readonly states = MONEY_STATES;
  protected readonly positions = POSITIONS;
  protected readonly accepting = MONEY_ACCEPTING;
  protected readonly edges = EDGES;
  protected readonly radius = RADIUS;
  protected readonly pattern = MONEY_PATTERN;

  protected readonly trace = computed(() => {
    const value = this.value();
    return value ? traceMoney(value) : null;
  });

  protected readonly usedEdges = computed(() => new Set(this.trace()?.steps.map((step) => `${step.from}>${step.to}`) ?? []));

  private readonly visited = computed(() => new Set<MoneyState>(this.trace() ? ['q0', ...this.trace()!.steps.map((step) => step.to)] : []));

  protected stateClass(state: MoneyState): string {
    const trace = this.trace();
    if (trace && state === trace.last) {
      return trace.accepted ? 'final-ok' : 'final-bad';
    }
    return this.visited().has(state) ? 'visited' : '';
  }
}
