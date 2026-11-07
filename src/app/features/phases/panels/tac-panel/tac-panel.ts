import { Component, input } from '@angular/core';

// Panel de la fase 4 · Responsable: Mora
@Component({
  selector: 'app-tac-panel',
  template: `
    <ol class="code-list">
      @for (line of lines(); track $index) {
        <li>{{ line }}</li>
      }
    </ol>
  `,
})
export class TacPanel {
  readonly lines = input<string[]>([]);
}
