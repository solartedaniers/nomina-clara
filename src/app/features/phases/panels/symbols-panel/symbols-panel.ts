import { Component, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SymbolDto } from '../../../../core/models/compile.models';

// Panel de la fase 3 · Responsable: Ramírez
@Component({
  selector: 'app-symbols-panel',
  imports: [TranslatePipe],
  template: `
    <table class="data-table">
      <thead>
        <tr>
          <th>{{ 'symbols.name' | t }}</th>
          <th>{{ 'symbols.type' | t }}</th>
          <th>{{ 'symbols.scope' | t }}</th>
          <th>{{ 'symbols.address' | t }}</th>
          <th>{{ 'symbols.kind' | t }}</th>
        </tr>
      </thead>
      <tbody>
        @for (symbol of symbols(); track $index) {
          <tr>
            <td class="mono">{{ symbol.name }}</td>
            <td>{{ symbol.type }}</td>
            <td><span class="scope-tag">{{ symbol.scope }}</span></td>
            <td class="mono">{{ symbol.address }}</td>
            <td>{{ symbol.kind }}</td>
          </tr>
        }
      </tbody>
    </table>
  `,
  styles: `
    .scope-tag {
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--surface-muted);
      font-size: 12px;
    }
  `,
})
export class SymbolsPanel {
  readonly symbols = input<SymbolDto[]>([]);
}
