import { Component, computed, input } from '@angular/core';

@Component({
  selector: 'app-json-view',
  template: `<pre class="code-block">{{ formatted() }}</pre>`,
})
export class JsonView {
  readonly value = input<unknown>(null);
  protected readonly formatted = computed(() => JSON.stringify(this.value(), null, 2));
}
