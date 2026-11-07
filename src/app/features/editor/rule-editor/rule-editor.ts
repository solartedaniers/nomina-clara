import { Component, computed, inject } from '@angular/core';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';
import { Icon } from '../../../shared/icon/icon';
import { highlightLine } from '../../../shared/syntax/syntax';

// Editor con resaltado: el texto coloreado va en una capa debajo y el textarea encima,
// con letra transparente, para que se pueda escribir normal y se vean los colores.
@Component({
  selector: 'app-rule-editor',
  imports: [TranslatePipe, Icon],
  template: `
    <section class="card">
      <header class="card-header">
        <div class="card-title">
          <span class="card-icon"><app-icon name="edit" /></span>
          <div>
            <h2>{{ 'editor.title' | t }}</h2>
            <p>{{ 'editor.hint' | t }}</p>
          </div>
        </div>
        <span class="pill">{{ 'editor.lines' | t: { count: lines().length } }}</span>
      </header>
      <div class="editor">
        <div class="gutter" aria-hidden="true" #gutter>
          @for (line of lines(); track $index) {
            @let number = $index + 1;
            <span
              [class.error-line]="number === errorLine()"
              [class.selected-line]="number === store.selectedLine()"
              (click)="store.selectedLine.set(number)"
            >{{ number }}</span>
          }
        </div>
        <div class="code-area">
          <pre class="highlight" aria-hidden="true" #highlight><div class="lines">@for (line of lines(); track $index) {@let number = $index + 1;<div class="code-line" [class.error-line]="number === errorLine()" [class.selected-line]="number === store.selectedLine()">@for (piece of line; track $index) {<span [class]="piece.cls">{{ piece.text }}</span>}</div>}</div></pre>
          <textarea
            spellcheck="false"
            [value]="store.source()"
            (input)="onInput($event)"
            (scroll)="syncScroll($event, gutter, highlight)"
            (click)="selectCaretLine($event)"
            (keyup)="selectCaretLine($event)"
            [attr.aria-label]="'editor.title' | t"
          ></textarea>
        </div>
      </div>
      <p class="hint footer">{{ 'editor.selectHint' | t }}</p>
      @if (store.blockingError(); as error) {
        <p class="error-box">
          <strong>{{ 'errors.' + error.phase | t }}</strong>
          @if (error.line) {
            · {{ 'editor.position' | t: { line: error.line, col: error.col } }}
          }
          <br />{{ error.message }}
        </p>
      }
    </section>
  `,
  styles: `
    .editor {
      display: grid;
      grid-template-columns: 44px 1fr;
      height: 360px;
      overflow: hidden;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: #fbfcfe;
      font: 13px/21px var(--mono);
      font-variant-ligatures: none;
    }
    .gutter {
      display: flex;
      flex-direction: column;
      padding: 10px 0 34px;
      overflow: hidden;
      background: #f3f6fa;
      border-right: 1px solid var(--border);
      color: #a3aec2;
      text-align: right;
      user-select: none;
    }
    .gutter span {
      padding-right: 10px;
      cursor: pointer;
    }
    .gutter span:hover {
      color: var(--brand);
    }
    .code-area {
      position: relative;
      min-width: 0;
    }
    .highlight,
    textarea {
      position: absolute;
      inset: 0;
      margin: 0;
      border: 0;
      font: inherit;
      white-space: pre;
      tab-size: 4;
    }
    .highlight {
      padding: 10px 0;
      overflow: hidden;
      color: var(--text);
    }
    /* Espacio extra para que la capa pueda desplazarse tanto como el textarea con sus barras */
    .lines {
      display: inline-block;
      min-width: 100%;
    }
    .lines::after {
      content: '';
      display: block;
      height: 24px;
    }
    .code-line {
      min-height: 21px;
      padding: 0 24px 0 12px;
    }
    textarea {
      width: 100%;
      height: 100%;
      padding: 10px 12px;
      resize: none;
      outline: none;
      overflow: auto;
      color: transparent;
      background: transparent;
      caret-color: var(--text);
    }
    textarea::selection {
      color: transparent;
      background: rgba(59, 130, 246, 0.25);
    }
    .selected-line {
      background: #e8f0fe;
    }
    .gutter .selected-line {
      background: #d6e4fd;
      color: var(--brand);
      font-weight: 700;
      box-shadow: inset 3px 0 0 var(--brand);
    }
    .error-line {
      background: #fde8e8;
    }
    .gutter .error-line {
      background: #fbd5d5;
      color: var(--danger);
      font-weight: 700;
      box-shadow: inset 3px 0 0 var(--danger);
    }
    .footer {
      margin: 8px 0 0;
    }
  `,
})
export class RuleEditor {
  protected readonly store = inject(WorkspaceStore);

  protected readonly lines = computed(() => this.store.source().split('\n').map(highlightLine));

  protected readonly errorLine = computed(() => this.store.blockingError()?.line ?? 0);

  protected syncScroll(event: Event, gutter: HTMLElement, highlight: HTMLElement): void {
    const textarea = event.target as HTMLTextAreaElement;
    gutter.scrollTop = textarea.scrollTop;
    highlight.scrollTop = textarea.scrollTop;
    highlight.scrollLeft = textarea.scrollLeft;
  }

  // La línea donde está el cursor es la que se sigue en el "viaje de una línea"
  protected selectCaretLine(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    this.store.selectedLine.set(textarea.value.slice(0, textarea.selectionStart).split('\n').length);
  }

  protected onInput(event: Event): void {
    this.store.source.set((event.target as HTMLTextAreaElement).value);
  }
}
