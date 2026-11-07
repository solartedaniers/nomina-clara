import { Component, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { MemoryDto } from '../../../../core/models/compile.models';
import { JsonView } from '../../../../shared/json-view/json-view';

// Panel de la fase 5 · Responsable: Ramírez
// TODO (Ramírez): animar los eventos push/pop de memory.events paso a paso
@Component({
  selector: 'app-memory-panel',
  imports: [JsonView, TranslatePipe],
  template: `
    @if (memory(); as memory) {
      <div class="memory-grid">
        <div>
          <h3>{{ 'memory.data' | t }}</h3>
          <app-json-view [value]="memory.data" />
        </div>
        <div>
          <h3>{{ 'memory.stack' | t }}</h3>
          <app-json-view [value]="memory.stack" />
        </div>
        <div>
          <h3>{{ 'memory.heap' | t }}</h3>
          <app-json-view [value]="memory.heap" />
        </div>
        <div>
          <h3>{{ 'memory.events' | t }}</h3>
          <app-json-view [value]="memory.events" />
        </div>
      </div>
    }
  `,
  styles: `
    .memory-grid {
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
export class MemoryPanel {
  readonly memory = input<MemoryDto | undefined>(undefined);
}
