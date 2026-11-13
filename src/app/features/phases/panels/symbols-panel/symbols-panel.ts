import { Component, computed, input } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SymbolDto } from '../../../../core/models/compile.models';

// Panel de la fase 3 · Responsable: Ramírez
// Tabla de símbolos agrupada por ámbito, con un color por ámbito (global, función, empleado, si...)
const SCOPE_COLORS = ['#1f3a68', '#7c3aed', '#0e7490', '#b45309', '#be185d', '#15803d', '#4338ca'];

@Component({
  selector: 'app-symbols-panel',
  imports: [TranslatePipe],
  template: `
    <div class="legend">
      @for (scope of scopes(); track scope) {
        <span class="scope-tag" [style.--scope]="color(scope)">{{ scope }}</span>
      }
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>{{ 'symbols.name' | t }}</th>
          <th>{{ 'symbols.type' | t }}</th>
          <th>{{ 'symbols.scope' | t }}</th>
          <th>{{ 'symbols.address' | t }}</th>
          <th>{{ 'symbols.kind' | t }}</th>
          <th>{{ 'symbols.line' | t }}</th>
        </tr>
      </thead>
      <tbody>
        @for (symbol of grouped(); track $index) {
          <tr [style.--scope]="color(symbol.scope)">
            <td class="mono name">{{ symbol.name }}</td>
            <td>{{ symbol.type }}</td>
            <td><span class="scope-tag">{{ symbol.scope }}</span></td>
            <td class="mono">{{ symbol.address }}</td>
            <td>{{ symbol.kind }}</td>
            <td class="mono">{{ symbol.line }}</td>
          </tr>
        }
      </tbody>
    </table>
  `,
  styles: `
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
    }
    .scope-tag {
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      color: #fff;
      background: var(--scope, var(--brand));
    }
    tr td.name {
      border-left: 4px solid var(--scope, var(--brand));
    }
  `,
})
export class SymbolsPanel {
  readonly symbols = input<SymbolDto[]>([]);

  // Ámbitos en el orden en que aparecen (global primero)
  protected readonly scopes = computed(() => [...new Set(this.symbols().map((symbol) => symbol.scope))]);
  protected readonly grouped = computed(() => {
    const order = this.scopes();
    return [...this.symbols()].sort((a, b) => order.indexOf(a.scope) - order.indexOf(b.scope));
  });

  protected color(scope: string): string {
    const index = this.scopes().indexOf(scope);
    return SCOPE_COLORS[(index < 0 ? 0 : index) % SCOPE_COLORS.length];
  }
}
