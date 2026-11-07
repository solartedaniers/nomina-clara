import { Component, computed, inject, input, signal } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { TokenDto } from '../../../../core/models/compile.models';
import { WorkspaceStore } from '../../../../core/services/workspace.store';
import { syntaxClass } from '../../../../shared/syntax/syntax';
import { MoneyDfa } from './money-dfa/money-dfa';

// Leyenda: mismos colores que el resaltado del editor
const LEGEND = ['keyword', 'type', 'money', 'number', 'string', 'identifier', 'operator', 'punct'];

// Panel de la fase 1 · Responsable: Daniers
@Component({
  selector: 'app-tokens-panel',
  imports: [TranslatePipe, MoneyDfa],
  template: `
    @if (tokens().length) {
      <div class="toolbar">
        <span class="pill">{{ 'tokens.count' | t: { count: tokens().length } }}</span>
        <p class="legend">
          @for (item of legend; track item) {
            <span [class]="'syn-' + item">{{ 'tokens.legend.' + item | t }}</span>
          }
        </p>
      </div>
      <div class="token-lines">
        @for (group of groups(); track group.line) {
          <div class="token-line" [class.selected]="group.line === store.selectedLine()" (click)="store.selectedLine.set(group.line)">
            <span class="line-number">{{ group.line }}</span>
            @for (token of group.tokens; track $index) {
              <span class="token-chip" [class]="'token-chip ' + classOf(token.type)" [title]="token.line + ':' + token.col"
                [class.picked]="token.type === 'MONEY' && token.value === selectedMoney()"
                (click)="token.type === 'MONEY' && selectedMoney.set(token.value)">
                <small>{{ token.type }}</small>{{ token.value || '∅' }}
              </span>
            }
          </div>
        }
      </div>
      <app-money-dfa [value]="selectedMoney()" />
    }
  `,
  styles: `
    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 4px 12px;
      margin: 0;
      font-size: 11.5px;
    }
    .legend span::before {
      content: '';
      display: inline-block;
      width: 10px;
      height: 10px;
      margin-right: 5px;
      border-radius: 3px;
      background: currentColor;
      vertical-align: -1px;
    }
    .token-lines {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 4px 8px;
    }
    .token-line {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 5px;
      padding: 5px 4px;
      border-bottom: 1px dashed var(--border-soft);
      border-radius: 6px;
      cursor: pointer;
    }
    .token-line:last-child {
      border-bottom: 0;
    }
    .token-line.selected {
      background: #e8f0fe;
    }
    .token-chip.picked {
      outline: 2px solid #15803d;
      outline-offset: 1px;
    }
    .line-number {
      width: 26px;
      font: 600 11px var(--mono);
      color: #a3aec2;
    }
  `,
})
export class TokensPanel {
  readonly tokens = input<TokenDto[]>([]);
  protected readonly store = inject(WorkspaceStore);
  protected readonly legend = LEGEND;
  protected readonly classOf = syntaxClass;
  // Valor MONEY elegido para resaltar su recorrido en el autómata
  protected readonly selectedMoney = signal<string | null>(null);

  protected readonly groups = computed(() => {
    const groups: { line: number; tokens: TokenDto[] }[] = [];
    for (const token of this.tokens()) {
      const last = groups.at(-1);
      if (last?.line === token.line) {
        last.tokens.push(token);
      } else {
        groups.push({ line: token.line, tokens: [token] });
      }
    }
    return groups;
  });
}
