import { Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { TacDto, TacInstructionDto } from '../../../../core/models/compile.models';

// Panel de la fase 4 · Responsable: Mora
// TAC numerado, con la línea del programa que generó cada instrucción y colores por tipo de instrucción

const TEMP = /\bt\d+\b/g;

export function tacKind(op: string): string {
  if (op === 'label') return 'label';
  if (op === 'ifFalse' || op === 'goto') return 'jump';
  if (op === 'param' || op === 'call' || op === 'return') return 'call';
  if (op === 'pay') return 'pay';
  if (op.startsWith('begin_') || op.startsWith('end_')) return 'marker';
  return 'operation';
}

@Component({
  selector: 'app-tac-panel',
  imports: [TranslatePipe],
  template: `
    <div class="summary">
      <span class="chip">{{ 'tac.instructions' | t: { count: rows().length } }}</span>
      <span class="chip temp">{{ 'tac.temps' | t: { count: temps() } }}</span>
      <span class="chip label">{{ 'tac.labels' | t: { count: labels() } }}</span>
    </div>
    <ol class="code-list tac">
      @for (row of rows(); track $index) {
        <li [class]="row.kind">
          <span class="text">{{ row.text }}</span>
          @if (row.line) {
            <span class="source" [title]="'tac.line' | t">L{{ row.line }}</span>
          }
        </li>
      }
    </ol>
  `,
  styles: `
    .summary {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }
    .chip {
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      background: var(--brand-soft);
      color: var(--brand);
    }
    .chip.temp {
      background: #f3e8ff;
      color: #7c3aed;
    }
    .chip.label {
      background: #fef3c7;
      color: #b45309;
    }
    .source {
      float: right;
      margin-left: 12px;
      color: #a3aec2;
      font-size: 11px;
    }
    .label .text {
      font-weight: 700;
      color: #b45309;
    }
    .jump .text {
      color: #7c3aed;
    }
    .call .text {
      color: #0e7490;
    }
    .pay .text {
      font-weight: 700;
      color: var(--success);
    }
    .marker .text {
      color: var(--text-muted);
      font-style: italic;
    }
  `,
})
export class TacPanel {
  readonly tac = input<TacDto | undefined>(undefined);

  protected readonly rows = computed(() => {
    const tac = this.tac();
    if (!tac) return [];
    return tac.text.map((text, index) => {
      const instruction: TacInstructionDto | undefined = tac.tac[index];
      return { text, line: instruction?.line ?? null, kind: tacKind(instruction?.op ?? '') };
    });
  });

  protected readonly temps = computed(() => new Set(this.rows().flatMap((row) => row.text.match(TEMP) ?? [])).size);
  protected readonly labels = computed(() => this.rows().filter((row) => row.kind === 'label').length);
}
