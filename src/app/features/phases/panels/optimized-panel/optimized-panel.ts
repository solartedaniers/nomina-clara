import { Component, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { OptimizedDto } from '../../../../core/models/compile.models';

// Panel de la fase 6 · Responsable: Mora
@Component({
  selector: 'app-optimized-panel',
  imports: [TranslatePipe],
  template: `
    <div class="compare">
      <div>
        <h3>{{ 'optimizer.before' | t: { count: before().length } }}</h3>
        <ol class="code-list">
          @for (line of before(); track $index) {
            <li>{{ line }}</li>
          }
        </ol>
      </div>
      <div>
        <h3>{{ 'optimizer.after' | t: { count: optimized()?.optimizedCount ?? 0 } }}</h3>
        <ol class="code-list">
          @for (line of optimized()?.text ?? []; track $index) {
            <li>{{ line }}</li>
          }
        </ol>
      </div>
    </div>
    @if (optimized()?.steps?.length) {
      <h3>{{ 'optimizer.steps' | t }}</h3>
      <ul>
        @for (step of optimized()?.steps; track $index) {
          <li>{{ step }}</li>
        }
      </ul>
    }
  `,
  styles: `
    .compare {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    h3 {
      margin: 0 0 6px;
      font-size: 13px;
    }
  `,
})
export class OptimizedPanel {
  readonly before = input<string[]>([]);
  readonly optimized = input<OptimizedDto | undefined>(undefined);
}
