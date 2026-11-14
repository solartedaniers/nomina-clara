import { Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { OptimizedDto } from '../../../../core/models/compile.models';

// Panel de la fase 6 · Responsable: Mora
// TAC antes y después lado a lado; las líneas que desaparecen o cambian quedan marcadas

type StepKind = 'folding' | 'propagation' | 'copies';

function stepKind(step: string): StepKind {
  if (step.startsWith('Plegado')) return 'folding';
  if (step.startsWith('Propagación')) return 'propagation';
  return 'copies';
}

@Component({
  selector: 'app-optimized-panel',
  imports: [TranslatePipe],
  template: `
    @if (optimized(); as result) {
      <div class="summary">
        <span class="chip saved">{{ 'optimizer.removed' | t: { count: result.removed } }}</span>
        @for (kind of kinds; track kind) {
          <span [class]="'chip ' + kind">{{ 'optimizer.kinds.' + kind | t }}: {{ countOf(kind) }}</span>
        }
      </div>
    }
    <div class="compare">
      <div>
        <h3>{{ 'optimizer.before' | t: { count: before().length } }}</h3>
        <ol class="code-list">
          @for (line of before(); track $index) {
            <li [class.gone]="!afterSet().has(line)">{{ line }}</li>
          }
        </ol>
      </div>
      <div>
        <h3>{{ 'optimizer.after' | t: { count: optimized()?.optimizedCount ?? 0 } }}</h3>
        <ol class="code-list">
          @for (line of optimized()?.text ?? []; track $index) {
            <li [class.new]="!beforeSet().has(line)">{{ line }}</li>
          }
        </ol>
      </div>
    </div>
    <h3>{{ 'optimizer.steps' | t }}</h3>
    @if (steps().length) {
      <ul class="steps">
        @for (step of steps(); track $index) {
          <li><span [class]="'tag ' + step.kind">{{ 'optimizer.kinds.' + step.kind | t }}</span>{{ step.detail }}</li>
        }
      </ul>
    } @else {
      <p class="muted">{{ 'optimizer.noChanges' | t }}</p>
    }
  `,
  styles: `
    .summary {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }
    .chip,
    .tag {
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
    }
    .saved {
      background: var(--success-soft);
      color: var(--success);
      font-weight: 600;
    }
    .folding {
      background: #e0f2fe;
      color: #0369a1;
    }
    .propagation {
      background: #f3e8ff;
      color: #7c3aed;
    }
    .copies {
      background: #fef3c7;
      color: #b45309;
    }
    .compare {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    h3 {
      margin: 10px 0 6px;
      font-size: 13px;
    }
    .gone {
      color: var(--danger);
      text-decoration: line-through;
    }
    .new {
      color: var(--success);
      font-weight: 600;
    }
    .steps {
      margin: 0;
      padding-left: 0;
      list-style: none;
      font: 12px var(--mono);
      font-variant-ligatures: none;
    }
    .steps li {
      display: flex;
      align-items: baseline;
      gap: 8px;
      padding: 3px 0;
    }
    .tag {
      flex: none;
      font-family: inherit;
      font-size: 11px;
    }
    .muted {
      color: var(--text-muted);
      font-size: 13px;
    }
  `,
})
export class OptimizedPanel {
  readonly before = input<string[]>([]);
  readonly optimized = input<OptimizedDto | undefined>(undefined);

  protected readonly kinds: StepKind[] = ['folding', 'propagation', 'copies'];

  protected readonly beforeSet = computed(() => new Set(this.before()));
  protected readonly afterSet = computed(() => new Set(this.optimized()?.text ?? []));

  // Quita el prefijo "Plegado de constantes: " porque el tipo ya va en la etiqueta de color
  protected readonly steps = computed(() =>
    (this.optimized()?.steps ?? []).map((step) => ({ kind: stepKind(step), detail: step.slice(step.indexOf(':') + 1).trim() })),
  );

  protected countOf(kind: StepKind): number {
    return this.steps().filter((step) => step.kind === kind).length;
  }
}
