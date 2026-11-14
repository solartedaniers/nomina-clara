import { Component, computed, input, signal } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { AssemblyDto } from '../../../../core/models/compile.models';

// Panel de la fase 7 · Responsable: Mora
// Ensamblador con los registros R0, R1 y R2, los spills marcados en rojo
// y la comparación del opcional (liberar registros de temporales que ya no se usan)

const JUMPS = /^(JMP|JG|JGE|JL|JLE|JE|JNE|CALL|RET)\b/;

@Component({
  selector: 'app-assembly-panel',
  imports: [TranslatePipe],
  template: `
    @if (assembly()?.registers; as registers) {
      <h3>{{ 'assembly.registers' | t }}</h3>
      <div class="registers">
        @for (name of registerNames; track name) {
          <div class="register" [class.busy]="registers[name]">
            <b>{{ name }}</b>
            <span>{{ registers[name] ?? ('assembly.free' | t) }}</span>
          </div>
        }
      </div>
    }

    <ol class="code-list">
      @for (line of lines(); track $index) {
        <li [class]="lineClass(line)">{{ line }}</li>
      }
    </ol>

    @if (spillCount() > 0) {
      <p class="spill-note">{{ 'assembly.spills' | t: { count: spillCount() } }}</p>
      <h3>{{ 'assembly.spillTable' | t }}</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ 'assembly.variable' | t }}</th>
            <th>{{ 'assembly.register' | t }}</th>
            <th>{{ 'assembly.address' | t }}</th>
          </tr>
        </thead>
        <tbody>
          @for (spill of assembly()?.spills ?? []; track $index) {
            <tr>
              <td class="mono">{{ spill.variable }}</td>
              <td class="mono">{{ spill.register }}</td>
              <td class="mono">{{ spill.address }}</td>
            </tr>
          }
        </tbody>
      </table>
    }

    @if (assembly()?.comparison; as comparison) {
      <h3>{{ 'assembly.comparison' | t }}</h3>
      <div class="comparison">
        <span class="chip professor">{{ 'assembly.professor' | t: { count: comparison.professorSpills } }}</span>
        <span class="chip freeing">{{ 'assembly.freeing' | t: { count: comparison.freeingSpills } }}</span>
        <button type="button" class="link" (click)="showFreeing.set(!showFreeing())">
          {{ (showFreeing() ? 'assembly.showProfessor' : 'assembly.showFreeing') | t }}
        </button>
      </div>
    }

    @if (assembly()?.unsupported?.length) {
      <h3>{{ 'assembly.unsupported' | t }}</h3>
      <ol class="code-list muted">
        @for (line of assembly()?.unsupported; track $index) {
          <li>{{ line }}</li>
        }
      </ol>
    }
  `,
  styles: `
    h3 {
      font-size: 13px;
      margin: 12px 0 6px;
    }
    .registers {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }
    .register {
      display: flex;
      justify-content: space-between;
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface-muted);
      font: 12px var(--mono);
      color: var(--text-muted);
    }
    .register.busy {
      border-color: var(--brand);
      background: var(--brand-soft);
      color: var(--brand);
    }
    .spill-line {
      color: var(--danger);
      font-weight: 600;
    }
    .spill-read {
      color: var(--danger);
    }
    .label-line {
      color: #b45309;
      font-weight: 700;
    }
    .jump-line {
      color: #7c3aed;
    }
    .spill-note {
      color: var(--danger);
      font-size: 13px;
    }
    .muted {
      color: var(--text-muted);
    }
    .comparison {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .chip {
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
    }
    .professor {
      background: var(--danger-soft);
      color: var(--danger);
    }
    .freeing {
      background: var(--success-soft);
      color: var(--success);
    }
    .link {
      border: 0;
      background: none;
      color: var(--brand);
      font-size: 12px;
      text-decoration: underline;
      cursor: pointer;
    }
  `,
})
export class AssemblyPanel {
  readonly assembly = input<AssemblyDto | undefined>(undefined);

  protected readonly registerNames = ['R0', 'R1', 'R2'];
  protected readonly showFreeing = signal(false);

  protected readonly lines = computed(() => {
    const assembly = this.assembly();
    if (this.showFreeing() && assembly?.comparison) return assembly.comparison.freeingLines;
    return assembly?.lines ?? [];
  });

  protected readonly spillCount = computed(() => this.assembly()?.spills.length ?? 0);

  // Direcciones de la RAM usadas por los spills (0x2000, 0x2004...)
  private readonly spillAddresses = computed(() => (this.assembly()?.spills ?? []).map((spill) => `[${spill.address}]`));

  protected lineClass(line: string): string {
    if (line.startsWith('STORE') || line.startsWith('LOAD')) return 'spill-line';
    if (this.spillAddresses().some((address) => line.includes(address))) return 'spill-read';
    if (line.endsWith(':')) return 'label-line';
    if (JUMPS.test(line)) return 'jump-line';
    return '';
  }
}
