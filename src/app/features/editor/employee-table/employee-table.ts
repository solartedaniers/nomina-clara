import { Component, inject } from '@angular/core';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';

@Component({
  selector: 'app-employee-table',
  imports: [TranslatePipe],
  template: `
    <section class="card">
      <header class="card-header">
        <h2>{{ 'employees.title' | t }}</h2>
        <button type="button" class="button-secondary" (click)="store.addEmployee()">{{ 'employees.add' | t }}</button>
      </header>
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ 'employees.name' | t }}</th>
            <th>{{ 'employees.salary' | t }}</th>
            <th>{{ 'employees.overtime' | t }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (employee of store.employees(); track $index; let index = $index) {
            <tr>
              <td><input [value]="employee.nombre" (input)="update(index, 'nombre', $event)" /></td>
              <td><input type="number" min="0" [value]="employee.salario" (input)="update(index, 'salario', $event)" /></td>
              <td><input type="number" min="0" [value]="employee.extras" (input)="update(index, 'extras', $event)" /></td>
              <td>
                <button type="button" class="icon-button" (click)="store.removeEmployee(index)" [attr.aria-label]="'employees.remove' | t">×</button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </section>
  `,
  styles: `
    input {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px 8px;
      font: inherit;
      background: var(--surface);
    }
    td:last-child {
      width: 32px;
    }
  `,
})
export class EmployeeTable {
  protected readonly store = inject(WorkspaceStore);

  protected update(index: number, field: 'nombre' | 'salario' | 'extras', event: Event): void {
    const raw = (event.target as HTMLInputElement).value;
    const value = field === 'nombre' ? raw : Number(raw) || 0;
    this.store.updateEmployee(index, { [field]: value });
  }
}
