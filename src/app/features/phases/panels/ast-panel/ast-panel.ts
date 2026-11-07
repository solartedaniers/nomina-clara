import { Component, input } from '@angular/core';
import { JsonView } from '../../../../shared/json-view/json-view';

// Panel de la fase 2 · Responsable: Daniers
// TODO (Daniers): si sobra tiempo, dibujar el AST como árbol en vez de JSON
@Component({
  selector: 'app-ast-panel',
  imports: [JsonView],
  template: `<app-json-view [value]="ast()" />`,
})
export class AstPanel {
  readonly ast = input<Record<string, unknown> | undefined>(undefined);
}
