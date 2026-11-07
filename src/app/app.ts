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
import { Icon } from './shared/icon/icon';

@Component({
  selector: 'app-root',
  imports: [TranslatePipe, RuleEditor, EmployeeTable, PhaseBar, PhasePanel, PayrollTable, Icon],
  template: `
    <header class="top-bar">
      <div class="brand">
        <span class="logo" aria-hidden="true">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 2h9l4 4v16H6z M15 2v4h4 M9 11h7 M9 15h4" />
            <circle cx="16.5" cy="17.5" r="3.2" fill="#f2b630" stroke="#f2b630" />
            <path d="M16.5 16v3" stroke="#0b1f3a" stroke-width="1.4" />
          </svg>
        </span>
        <div>
          <h1>{{ 'app.title' | t }} <span class="course">{{ 'app.course' | t }}</span></h1>
          <p>{{ 'app.subtitle' | t }}</p>
        </div>
      </div>
      <div class="actions">
        <select (change)="onSampleChange($event)" [attr.aria-label]="'samples.label' | t">
          @for (sample of samples; track sample.id) {
            <option [value]="sample.id">{{ sample.labelKey | t }}</option>
          }
        </select>
        <button type="button" class="button-accent" [disabled]="store.loading()" (click)="store.compile()">
          <app-icon name="play" [size]="14" />
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

    <app-phase-bar class="pipeline" />

    <main class="workspace">
      <div class="column">
        <app-rule-editor />
        <app-employee-table />
      </div>
      <div class="column phase-column">
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
      color: #fff;
      background: linear-gradient(110deg, var(--brand-900), var(--brand) 70%, #284f8c);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.2px;
    }
    .brand p {
      margin: 2px 0 0;
      font-size: 12.5px;
      color: #c7d4ea;
    }
    .course {
      margin-left: 6px;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid rgba(242, 182, 48, 0.35);
      background: rgba(242, 182, 48, 0.16);
      color: #ffd77a;
      font-size: 11px;
      font-weight: 600;
      vertical-align: 3px;
    }
    .logo {
      display: grid;
      place-items: center;
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .actions {
      display: flex;
      gap: 10px;
    }
    select {
      border: 1px solid rgba(255, 255, 255, 0.22);
      border-radius: 10px;
      padding: 9px 12px;
      font: inherit;
      color: #fff;
      background: rgba(255, 255, 255, 0.08);
    }
    select option {
      color: var(--text);
    }
    .button-accent {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 0;
      border-radius: 10px;
      padding: 10px 16px;
      font: inherit;
      font-weight: 700;
      color: var(--brand-900);
      background: var(--accent);
      box-shadow: 0 2px 8px rgba(242, 182, 48, 0.35);
      cursor: pointer;
    }
    .button-accent:hover:not(:disabled) {
      background: var(--accent-hover);
    }
    .button-accent:disabled {
      opacity: 0.8;
      cursor: progress;
    }
    .banner {
      margin: 16px 24px 0;
    }
    .pipeline {
      display: block;
      padding: 16px 24px 0;
    }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
      gap: 16px;
      padding: 16px 24px 24px;
    }
    .column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    /* El panel de la fase ocupa todo el alto de la columna izquierda: así no queda espacio vacío */
    .phase-column {
      position: relative;
      min-height: 520px;
    }
    .phase-column app-phase-panel {
      position: absolute;
      inset: 0;
    }
    .full {
      grid-column: 1 / -1;
    }
    @media (max-width: 960px) {
      .workspace {
        grid-template-columns: 1fr;
      }
      .phase-column app-phase-panel {
        position: static;
      }
      .top-bar {
        flex-wrap: wrap;
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
