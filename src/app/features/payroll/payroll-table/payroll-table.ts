import { Component, computed, inject } from '@angular/core';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';

// Resultado de la ejecución · Responsable: Ramírez
@Component({
  selector: 'app-payroll-table',
  imports: [TranslatePipe],
  template: `
    <section class="card">
      <header class="card-header">
        <h2>{{ 'payroll.title' | t }}</h2>
        @if (entries().length) {
          <span class="total">{{ 'payroll.total' | t }}: {{ money(total()) }}</span>
        }
      </header>
      @if (entries().length) {
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ 'payroll.employee' | t }}</th>
              @for (column of columns(); track column) {
                <th class="number">{{ column }}</th>
              }
              <th class="number">{{ 'payroll.pay' | t }}</th>
            </tr>
          </thead>
          <tbody>
            @for (entry of entries(); track $index) {
              <tr>
                <td>{{ entry.name }}</td>
                @for (column of columns(); track column) {
                  <td class="number">{{ format(entry.values[column]) }}</td>
                }
                <td class="number strong">{{ money(entry.pay) }}</td>
              </tr>
            }
          </tbody>
        </table>
      } @else {
        <p class="empty">{{ 'payroll.empty' | t }}</p>
      }
    </section>
  `,
  styles: `
    .total {
      font-weight: 700;
      color: var(--brand);
    }
    .number,
    th.number {
      text-align: right;
      font-variant-numeric: tabular-nums;
    }
    .strong {
      font-weight: 700;
    }
    .empty {
      color: var(--text-muted);
    }
  `,
})
export class PayrollTable {
  private readonly store = inject(WorkspaceStore);
  private readonly formatter = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

  protected readonly entries = computed(() => this.store.response()?.payroll ?? []);
  protected readonly columns = computed(() => {
    const names = new Set<string>();
    this.entries().forEach((entry) => Object.keys(entry.values ?? {}).forEach((name) => names.add(name)));
    return [...names];
  });
  protected readonly total = computed(() => this.entries().reduce((sum, entry) => sum + (entry.pay ?? 0), 0));

  protected money(value: number): string {
    return this.formatter.format(value);
  }

  protected format(value: number | string | undefined): string {
    return typeof value === 'number' ? this.formatter.format(value) : (value ?? '');
  }
}
