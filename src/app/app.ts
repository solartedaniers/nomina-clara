import { Component, inject } from '@angular/core';
import { SAMPLE_PROGRAMS } from './core/data/sample-programs';
import { I18nService } from './core/i18n/i18n.service';
import { TranslatePipe } from './core/i18n/translate.pipe';
import { WorkspaceStore } from './core/services/workspace.store';
import { EmployeeTable } from './features/editor/employee-table/employee-table';
import { RuleEditor } from './features/editor/rule-editor/rule-editor';
import { PayrollTable } from './features/payroll/payroll-table/payroll-table';
import { PhaseBar } from './features/phases/phase-bar/phase-bar';
import { PhasePanel } from './features/phases/phase-panel/phase-panel';

@Component({
  selector: 'app-root',
  imports: [TranslatePipe, RuleEditor, EmployeeTable, PhaseBar, PhasePanel, PayrollTable],
  template: `
    <header class="top-bar">
      <div class="brand">
        <span class="logo">NC</span>
        <div>
          <h1>{{ 'app.title' | t }}</h1>
          <p>{{ 'app.subtitle' | t }}</p>
        </div>
      </div>
      <div class="actions">
        <select (change)="onSampleChange($event)" [attr.aria-label]="'samples.label' | t">
          @for (sample of samples; track sample.id) {
            <option [value]="sample.id">{{ sample.labelKey | t }}</option>
          }
        </select>
        <button type="button" class="button-primary" [disabled]="store.loading()" (click)="store.compile()">
          {{ (store.loading() ? 'app.compiling' : 'app.compile') | t }}
        </button>
      </div>
    </header>

    @if (store.requestFailed()) {
      <p class="error-box banner">{{ 'app.requestFailed' | t }}</p>
    }
    @if (store.pendingPhases().length) {
      <p class="warning-box banner">{{ 'app.pendingPhases' | t: { phases: pendingLabels() } }}</p>
    }

    <main class="workspace">
      <div class="column">
        <app-rule-editor />
        <app-employee-table />
      </div>
      <div class="column">
        <app-phase-bar />
        <app-phase-panel />
      </div>
      <div class="full">
        <app-payroll-table />
      </div>
    </main>
  `,
  styles: `
    .top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 14px 24px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand h1 {
      margin: 0;
      font-size: 18px;
    }
    .brand p {
      margin: 0;
      font-size: 12px;
      color: var(--text-muted);
    }
    .logo {
      display: grid;
      place-items: center;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: var(--brand);
      color: #fff;
      font-weight: 700;
    }
    .actions {
      display: flex;
      gap: 10px;
    }
    select {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 10px;
      font: inherit;
      background: var(--surface);
    }
    .banner {
      margin: 16px 24px 0;
    }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
      gap: 16px;
      padding: 16px 24px 32px;
    }
    .column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .full {
      grid-column: 1 / -1;
    }
    @media (max-width: 960px) {
      .workspace {
        grid-template-columns: 1fr;
      }
    }
  `,
})
export class App {
  protected readonly store = inject(WorkspaceStore);
  protected readonly samples = SAMPLE_PROGRAMS;
  private readonly i18n = inject(I18nService);

  protected pendingLabels(): string {
    return this.store
      .pendingPhases()
      .map((phase) => this.i18n.translate(`phases.${phase}.label`))
      .join(', ');
  }

  protected onSampleChange(event: Event): void {
    this.store.loadSample((event.target as HTMLSelectElement).value);
  }
}
