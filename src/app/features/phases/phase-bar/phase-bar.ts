import { Component, inject } from '@angular/core';
import { PHASE_DEFINITIONS } from '../../../core/data/phase-definitions';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';

// Ícono de cada estado; el color de la fase se mantiene y el estado se ve en el ícono y el borde
const STATUS_ICONS: Record<string, string> = { passed: '✓', failed: '✕', pending: '!', skipped: '–', idle: '–' };

@Component({
  selector: 'app-phase-bar',
  imports: [TranslatePipe],
  template: `
    <nav class="phase-bar" [attr.aria-label]="'phases.bar' | t">
      @for (phase of phases; track phase.key) {
        @let status = store.statusOf(phase.key) ?? 'idle';
        @let error = store.errorFor(phase.key);
        <button
          type="button"
          [class]="'phase-chip phase-' + phase.key + ' status-' + status"
          [class.selected]="store.selectedPhase() === phase.key"
          [attr.aria-pressed]="store.selectedPhase() === phase.key"
          (click)="store.selectedPhase.set(phase.key)"
        >
          <span class="title"><span class="phase-number">{{ phase.number }}</span>{{ phase.labelKey | t }}</span>
          <span class="week">{{ phase.weekKey | t }}</span>
          <span class="state">
            <span class="badge" aria-hidden="true">{{ icons[status] }}</span>
            @if (status === 'failed' && error?.line) {
              {{ 'status.failedAt' | t: { line: error!.line } }}
            } @else {
              {{ 'status.' + status | t }}
            }
          </span>
        </button>
      }
    </nav>
    <p class="legend">
      @for (status of legend; track status) {
        <span><i [class]="'status-' + status">{{ icons[status] }}</i>{{ 'phases.legend.' + status | t }}</span>
      }
    </p>
  `,
  styles: `
    .phase-bar {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 10px;
    }
    .phase-chip {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;
      padding: 12px 12px 10px;
      overflow: hidden;
      border-radius: 12px;
      border: 2px solid transparent;
      background: var(--surface);
      box-shadow: var(--shadow);
      font: inherit;
      text-align: left;
      color: var(--text);
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .phase-chip::before {
      content: '';
      position: absolute;
      inset: 0 0 auto;
      height: 4px;
      background: var(--phase-color);
    }
    .phase-chip:hover {
      transform: translateY(-1px);
    }
    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 13.5px;
      white-space: nowrap;
    }
    .week {
      margin-top: 4px;
      font-size: 11.5px;
      color: var(--text-muted);
    }
    .state {
      display: flex;
      align-items: center;
      gap: 5px;
      margin-top: 2px;
      font-size: 11px;
      font-weight: 600;
    }
    .badge,
    .legend i {
      display: grid;
      place-items: center;
      border-radius: 50%;
      color: #fff;
      font-weight: 800;
      font-style: normal;
    }
    .badge,
    .legend i {
      width: 16px;
      height: 16px;
      font-size: 10px;
    }
    .phase-chip.status-passed { border-color: var(--phase-color); }
    .phase-chip.status-failed { border-color: var(--danger); background: var(--danger-soft); }
    .phase-chip.status-pending { border: 2px dashed var(--warning); }
    .phase-chip.status-skipped, .phase-chip.status-idle { border: 2px dashed #cbd5e1; opacity: 0.65; }
    .status-passed .badge, i.status-passed { background: var(--success); }
    .status-failed .badge, i.status-failed { background: var(--danger); }
    .status-pending .badge, i.status-pending { background: var(--warning); }
    .status-skipped .badge, .status-idle .badge, i.status-skipped { background: #94a3b8; }
    .status-passed .state { color: var(--success); }
    .status-failed .state { color: var(--danger); }
    .status-pending .state { color: var(--warning); }
    .status-skipped .state, .status-idle .state { color: #94a3b8; }
    .phase-chip.selected {
      transform: translateY(-2px);
      box-shadow: 0 0 0 3px rgba(31, 58, 104, 0.2), var(--shadow);
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin: 8px 2px 0;
      font-size: 12px;
      color: var(--text-muted);
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    @media (max-width: 1100px) {
      .phase-bar {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }
    }
  `,
})
export class PhaseBar {
  protected readonly store = inject(WorkspaceStore);
  protected readonly phases = PHASE_DEFINITIONS;
  protected readonly icons = STATUS_ICONS;
  protected readonly legend = ['passed', 'failed', 'pending', 'skipped'];
}
