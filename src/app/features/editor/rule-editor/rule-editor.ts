import { Component, computed, inject } from '@angular/core';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { WorkspaceStore } from '../../../core/services/workspace.store';

@Component({
  selector: 'app-rule-editor',
  imports: [TranslatePipe],
  template: `
    <section class="card">
      <header class="card-header">
        <h2>{{ 'editor.title' | t }}</h2>
        <span class="hint">{{ 'editor.hint' | t }}</span>
      </header>
      <div class="editor">
        <div class="gutter" aria-hidden="true" #gutter>
          @for (line of lineNumbers(); track line) {
            <span [class.error-line]="line === errorLine()">{{ line }}</span>
          }
        </div>
        <textarea
          spellcheck="false"
          [value]="store.source()"
          (input)="onInput($event)"
          (scroll)="syncScroll($event, gutter)"
          [attr.aria-label]="'editor.title' | t"
        ></textarea>
      </div>
      @if (store.blockingError(); as error) {
        <p class="error-box">
          <strong>{{ 'errors.' + error.phase | t }}</strong>
          @if (error.line) {
            · {{ 'editor.line' | t: { line: error.line } }}
          }
          : {{ error.message }}
        </p>
      }
    </section>
  `,
  styles: `
    .editor {
      display: grid;
      grid-template-columns: 40px 1fr;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      font-family: var(--mono);
      font-variant-ligatures: none;
      font-size: 13px;
      line-height: 20px;
      height: 380px;
    }
    .gutter {
      display: flex;
      flex-direction: column;
      padding: 10px 6px;
      background: var(--surface-muted);
      color: var(--text-muted);
      text-align: right;
      overflow: hidden;
    }
    .gutter .error-line {
      color: var(--danger);
      font-weight: 700;
    }
    textarea {
      border: none;
      resize: none;
      padding: 10px;
      font: inherit;
      color: var(--text);
      background: var(--surface);
      outline: none;
      white-space: pre;
      overflow: auto;
    }
  `,
})
export class RuleEditor {
  protected readonly store = inject(WorkspaceStore);

  protected readonly lineNumbers = computed(() =>
    Array.from({ length: this.store.source().split('\n').length }, (_, index) => index + 1),
  );

  protected readonly errorLine = computed(() => this.store.blockingError()?.line ?? 0);

  protected syncScroll(event: Event, gutter: HTMLElement): void {
    gutter.scrollTop = (event.target as HTMLTextAreaElement).scrollTop;
  }

  protected onInput(event: Event): void {
    this.store.source.set((event.target as HTMLTextAreaElement).value);
  }
}
