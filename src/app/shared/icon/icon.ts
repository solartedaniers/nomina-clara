import { Component, computed, input } from '@angular/core';

// Íconos de línea propios (SVG en línea), para no agregar una librería de íconos
const PATHS: Record<string, string> = {
  logo: 'M6 2h9l4 4v16H6z M15 2v4h4 M9 11h7 M9 15h4',
  edit: 'M4 20h4L19 9l-4-4L4 16z M13.5 6.5l4 4',
  users: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M2 21v-1a6 6 0 0 1 12 0v1 M16 3.5a4 4 0 0 1 0 7.5 M18 15a6 6 0 0 1 4 5.5V21',
  play: 'M7 4l13 8-13 8z',
  tokens: 'M4 7h16 M4 12h10 M4 17h13',
  tree: 'M12 3v5 M12 8H6v4 M12 8h6v4 M4 12h4v4H4z M16 12h4v4h-4z M10 3h4',
  table: 'M3 5h18v14H3z M3 10h18 M9 10v9',
  code: 'M8 8l-4 4 4 4 M16 8l4 4-4 4 M13.5 5l-3 14',
  memory: 'M6 4h12v16H6z M9 8h6 M9 12h6 M9 16h3 M3 8h3 M3 16h3 M18 8h3 M18 16h3',
  bolt: 'M13 2L4 14h7l-1 8 9-12h-7z',
  chip: 'M7 7h10v10H7z M10 3v4 M14 3v4 M10 17v4 M14 17v4 M3 10h4 M3 14h4 M17 10h4 M17 14h4',
  route: 'M5 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4z M19 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4z M7 17h7a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h7',
  receipt: 'M6 2h12v20l-3-2-3 2-3-2-3 2z M9 7h6 M9 11h6 M9 15h3',
  cursor: 'M5 3l14 7-6 2-2 6z',
  hourglass: 'M7 3h10 M7 21h10 M8 3c0 5 8 5 8 9s-8 4-8 9 M16 3c0 5-8 5-8 9s8 4 8 9',
  alert: 'M12 3l10 18H2z M12 10v5 M12 18v.5',
  check: 'M5 12l5 5 9-10',
  close: 'M6 6l12 12 M18 6L6 18',
  minus: 'M6 12h12',
  plus: 'M12 6v12 M6 12h12',
};

@Component({
  selector: 'app-icon',
  template: `
    <svg [attr.width]="size()" [attr.height]="size()" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path [attr.d]="path()" />
    </svg>
  `,
  styles: `
    :host { display: inline-flex; }
  `,
})
export class Icon {
  readonly name = input.required<string>();
  readonly size = input(18);
  protected readonly path = computed(() => PATHS[this.name()] ?? '');
}
