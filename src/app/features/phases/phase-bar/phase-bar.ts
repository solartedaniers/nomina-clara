import { Component, inject } from '@angular/core';
import { PHASE_DEFINITIONS } from '../../../core/data/phase-definitions';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';

@Component({
  selector: 'app-phase-bar',
  imports: [TranslatePipe],
  template: `
    <nav class="phase-bar" [attr.aria-label]="'phases.bar' | t">
      @for (phase of phases; track phase.key) {
        <button
          type="button"
          class="phase-chip"
          [class]="'phase-chip status-' + (store.statusOf(phase.key) ?? 'idle')"
          [class.selected]="store.selectedPhase() === phase.key"
          (click)="store.selectedPhase.set(phase.key)"
        >
          <span class="number">{{ phase.number }}</span>
          <span class="label">{{ phase.labelKey | t }}</span>
        </button>
      }
    </nav>
    <p class="legend">{{ 'phases.legend' | t }}</p>
  `,
  styles: `
    .phase-bar {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
    }
    .phase-chip {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 8px 4px;
      border-radius: 8px;
      border: 1.5px solid var(--border);
      background: var(--surface);
      cursor: pointer;
      font: inherit;
      color: var(--text);
    }
    .phase-chip .number {
      font-weight: 700;
      font-size: 16px;
    }
    .phase-chip .label {
      font-size: 12px;
      color: var(--text-muted);
    }
    .phase-chip.selected {
      outline: 2px solid var(--brand);
      outline-offset: 2px;
    }
    .status-passed {
      background: var(--success-soft);
      border-color: var(--success);
    }
    .status-failed {
      background: var(--danger-soft);
      border-color: var(--danger);
    }
    .status-pending {
      background: var(--warning-soft);
      border-color: var(--warning);
    }
    .status-skipped,
    .status-idle {
      opacity: 0.75;
    }
    .legend {
      margin: 8px 0 0;
      font-size: 12px;
      color: var(--text-muted);
    }
  `,
})
export class PhaseBar {
  protected readonly store = inject(WorkspaceStore);
  protected readonly phases = PHASE_DEFINITIONS;
}
