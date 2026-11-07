import { Component, input } from '@angular/core';
import { TokenDto } from '../../../../core/models/compile.models';

// Panel de la fase 1 · Responsable: Daniers
@Component({
  selector: 'app-tokens-panel',
  template: `
    <div class="token-list">
      @for (token of tokens(); track $index) {
        <span class="token" [class]="'token token-' + token.type.toLowerCase()" [title]="token.line + ':' + token.col">
          <small>{{ token.type }}</small>{{ token.value }}
        </span>
      }
    </div>
  `,
  styles: `
    .token-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .token {
      display: inline-flex;
      align-items: baseline;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--surface-muted);
      font-family: var(--mono);
      font-size: 12px;
    }
    .token small {
      font-size: 10px;
      color: var(--text-muted);
    }
    .token-keyword { background: #e8f0fe; border-color: #a8c1f5; }
    .token-type { background: #f3e8fd; border-color: #cfaef0; }
    .token-identifier { background: #e7f6ec; border-color: #a6dbb7; }
    .token-money, .token-decimal, .token-integer { background: #fff4e0; border-color: #f2cf8a; }
  `,
})
export class TokensPanel {
  readonly tokens = input<TokenDto[]>([]);
}
