import { Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { AssemblyDto } from '../../../../core/models/compile.models';

// Panel de la fase 7 · Responsable: Mora
@Component({
  selector: 'app-assembly-panel',
  imports: [TranslatePipe],
  template: `
    <ol class="code-list">
      @for (line of assembly()?.lines ?? []; track $index) {
        <li [class.spill-line]="isSpill(line)">{{ line }}</li>
      }
    </ol>
    @if (spillCount() > 0) {
      <p class="spill-note">{{ 'assembly.spills' | t: { count: spillCount() } }}</p>
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
    .spill-line {
      color: var(--danger);
      font-weight: 600;
    }
    .spill-note {
      color: var(--danger);
      font-size: 13px;
    }
    .muted {
      color: var(--text-muted);
    }
    h3 {
      font-size: 13px;
      margin: 12px 0 6px;
    }
  `,
})
export class AssemblyPanel {
  readonly assembly = input<AssemblyDto | undefined>(undefined);
  protected readonly spillCount = computed(() => this.assembly()?.spills.length ?? 0);

  protected isSpill(line: string): boolean {
    return line.startsWith('STORE') || line.startsWith('LOAD');
  }
}
