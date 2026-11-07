import { Component, computed, inject } from '@angular/core';
import { PHASE_DEFINITIONS } from '../../../core/data/phase-definitions';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';
import { AssemblyPanel } from '../panels/assembly-panel/assembly-panel';
import { AstPanel } from '../panels/ast-panel/ast-panel';
import { MemoryPanel } from '../panels/memory-panel/memory-panel';
import { OptimizedPanel } from '../panels/optimized-panel/optimized-panel';
import { SymbolsPanel } from '../panels/symbols-panel/symbols-panel';
import { TacPanel } from '../panels/tac-panel/tac-panel';
import { TokensPanel } from '../panels/tokens-panel/tokens-panel';
import { Icon } from '../../../shared/icon/icon';

// Ícono de cada fase en el encabezado del panel
const PHASE_ICONS: Record<string, string> = {
  lexer: 'tokens',
  parser: 'tree',
  semantic: 'table',
  ir: 'code',
  memory: 'memory',
  optimizer: 'bolt',
  codegen: 'chip',
};

@Component({
  selector: 'app-phase-panel',
  imports: [TranslatePipe, Icon, TokensPanel, AstPanel, SymbolsPanel, TacPanel, MemoryPanel, OptimizedPanel, AssemblyPanel],
  template: `
    <section class="card panel">
      <header class="card-header">
        <div class="card-title">
          <span class="card-icon"><app-icon [name]="icon()" /></span>
          <div>
            <h2>{{ 'phases.prefix' | t: { number: definition().number } }} · {{ definition().titleKey | t }}</h2>
            <p>{{ definition().weekKey | t }}</p>
          </div>
        </div>
      </header>
      <div class="panel-body">

      @switch (status()) {
        @case (null) {
          <p class="empty-state">
            <span class="empty-icon"><app-icon name="cursor" [size]="22" /></span>
            <span><strong>{{ 'panel.idle.title' | t }}</strong>{{ 'panel.idle.text' | t }}</span>
          </p>
        }
        @case ('pending') {
          <p class="empty-state pending">
            <span class="empty-icon"><app-icon name="hourglass" [size]="22" /></span>
            <span><strong>{{ 'panel.pending.title' | t }}</strong>{{ 'panel.pending.text' | t: { week: (definition().weekKey | t) } }}</span>
          </p>
        }
        @case ('skipped') {
          <p class="empty-state">
            <span class="empty-icon"><app-icon name="route" [size]="22" /></span>
            <span><strong>{{ 'panel.skipped.title' | t }}</strong>{{ 'panel.skipped.text' | t }}</span>
          </p>
        }
        @default {
          @if (status() === 'failed') {
            <p class="error-box">{{ failureMessage() }}</p>
          }
          @let phases = store.response()?.phases;
          @switch (definition().key) {
            @case ('lexer') {
              <app-tokens-panel [tokens]="phases?.tokens ?? []" />
            }
            @case ('parser') {
              <app-ast-panel [ast]="phases?.ast" />
            }
            @case ('semantic') {
              <app-symbols-panel [symbols]="phases?.symbols ?? []" />
            }
            @case ('ir') {
              <app-tac-panel [lines]="phases?.tac?.text ?? []" />
            }
            @case ('memory') {
              <app-memory-panel [memory]="phases?.memory" />
            }
            @case ('optimizer') {
              <app-optimized-panel [before]="phases?.tac?.text ?? []" [optimized]="phases?.optimized" />
            }
            @case ('codegen') {
              <app-assembly-panel [assembly]="phases?.assembly" />
            }
          }
        }
      }
      </div>
    </section>
  `,
  styles: `
    :host {
      display: block;
    }
    .panel {
      height: 100%;
      min-height: 360px;
      display: flex;
      flex-direction: column;
    }
    .panel-body {
      flex: 1;
      min-height: 0;
      overflow: auto;
    }
  `,
})
export class PhasePanel {
  protected readonly store = inject(WorkspaceStore);
  private readonly i18n = inject(I18nService);

  protected readonly definition = computed(
    () => PHASE_DEFINITIONS.find((phase) => phase.key === this.store.selectedPhase()) ?? PHASE_DEFINITIONS[0],
  );

  protected readonly icon = computed(() => PHASE_ICONS[this.definition().key]);

  protected readonly status = computed(() => this.store.statusOf(this.definition().key));

  protected readonly failureMessage = computed(() => {
    const error = this.store.errorFor(this.definition().key);
    return error ? `${error.message}${error.line ? ` (${this.i18n.translate('editor.line', { line: error.line })})` : ''}` : '';
  });
}
