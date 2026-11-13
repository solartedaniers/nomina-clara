import { Component, computed, effect, input, OnDestroy, signal } from '@angular/core';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { MemoryDto } from '../../../../core/models/compile.models';
import { JsonView } from '../../../../shared/json-view/json-view';

interface MemoryEvent {
  step: number;
  action: string;
  function?: string;
  name?: string;
  value?: unknown;
  address?: string;
  description?: string;
  stack: string[];
  heap: string[];
}

// Panel de la fase 5 · Responsable: Ramírez
// Pila animada paso a paso con memory.events (push / pop / alloc / free) y el mapa Data · Stack · Heap
@Component({
  selector: 'app-memory-panel',
  imports: [JsonView, TranslatePipe],
  template: `
    @if (memory(); as memory) {
      @if (events().length) {
        <div class="player">
          <button type="button" (click)="move(-1)" [disabled]="index() === 0">◀</button>
          <button type="button" (click)="toggle()">{{ (playing() ? 'memory.pause' : 'memory.play') | t }}</button>
          <button type="button" (click)="move(1)" [disabled]="index() === events().length - 1">▶</button>
          <input type="range" min="0" [max]="events().length - 1" [value]="index()" (input)="seek($event)" />
          <span class="mono">{{ 'memory.step' | t: { step: index() + 1, total: events().length } }}</span>
        </div>
        <p [class]="'event mono ' + (current()?.action ?? '')">{{ describe(current()) }}</p>
      }

      <div class="memory-grid">
        <div>
          <h3>{{ 'memory.stack' | t }}</h3>
          <div class="stack">
            @for (frame of stackAtStep(); track $index; let top = $last) {
              <div class="frame" [class.top]="top">
                <strong>{{ frame }}</strong>
                @if (top) { <span class="tag">← cima</span> }
              </div>
            } @empty {
              <p class="muted">—</p>
            }
          </div>
        </div>
        <div>
          <h3>{{ 'memory.heap' | t }}</h3>
          @for (address of current()?.heap ?? []; track address) {
            <div class="frame heap mono">{{ address }} · {{ heapLabel(address) }}</div>
          } @empty {
            <p class="muted">—</p>
          }
          <h3>{{ 'memory.data' | t }}</h3>
          <table class="data-table">
            @for (item of memory.data; track item.name) {
              <tr><td class="mono">{{ item.name }}</td><td class="mono">{{ item.value }}</td></tr>
            }
          </table>
        </div>
      </div>

      <h3>{{ 'memory.peak' | t }}</h3>
      <app-json-view [value]="memory.stack" />
    }
  `,
  styles: `
    .player {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }
    .player input {
      flex: 1;
    }
    .event {
      margin: 0 0 10px;
      padding: 6px 10px;
      border-radius: 6px;
      background: var(--surface-muted);
    }
    .event.push { border-left: 4px solid var(--success); }
    .event.pop { border-left: 4px solid var(--brand); }
    .event.overflow { border-left: 4px solid #dc2626; color: #dc2626; }
    .memory-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .stack {
      display: flex;
      flex-direction: column-reverse;
      gap: 4px;
    }
    .frame {
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      animation: enter 0.25s ease-out;
    }
    .frame.top {
      border-color: var(--brand);
      background: var(--brand-soft);
    }
    .frame.heap {
      margin-bottom: 8px;
    }
    .tag {
      float: right;
      font-size: 12px;
      color: var(--brand);
    }
    .muted {
      color: var(--text-muted);
    }
    h3 {
      margin: 8px 0 6px;
      font-size: 13px;
    }
    @keyframes enter {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: none; }
    }
  `,
})
export class MemoryPanel implements OnDestroy {
  readonly memory = input<MemoryDto | undefined>(undefined);

  protected readonly index = signal(0);
  protected readonly playing = signal(false);
  private timer?: ReturnType<typeof setInterval>;

  protected readonly events = computed(() => (this.memory()?.events ?? []) as unknown as MemoryEvent[]);
  protected readonly current = computed(() => this.events()[this.index()]);
  protected readonly stackAtStep = computed(() => this.current()?.stack ?? []);

  constructor() {
    // Cada compilación nueva reinicia la animación desde el primer evento
    effect(() => {
      this.memory();
      this.stop();
      this.index.set(0);
    });
  }

  protected move(delta: number): void {
    const last = this.events().length - 1;
    this.index.update((value) => Math.min(last, Math.max(0, value + delta)));
  }

  protected seek(event: Event): void {
    this.index.set(Number((event.target as HTMLInputElement).value));
  }

  protected toggle(): void {
    if (this.playing()) {
      this.stop();
      return;
    }
    if (this.index() >= this.events().length - 1) {
      this.index.set(0);
    }
    this.playing.set(true);
    this.timer = setInterval(() => {
      if (this.index() >= this.events().length - 1) {
        this.stop();
      } else {
        this.move(1);
      }
    }, 700);
  }

  protected describe(event: MemoryEvent | undefined): string {
    if (!event) {
      return '';
    }
    switch (event.action) {
      case 'push':
        return `[STACK] push · entra el frame '${event.function}'`;
      case 'pop':
        return `[STACK] pop · sale el frame '${event.function}'`;
      case 'data':
        return `[DATA] ${event.name} = ${event.value}`;
      case 'alloc':
        return `[HEAP] reserva ${event.address} · ${event.description}`;
      case 'free':
        return `[HEAP] libera ${event.address}`;
      case 'overflow':
        return `[STACK] ¡Stack Overflow simulado al llamar a '${event.function}'!`;
      default:
        return event.action;
    }
  }

  protected heapLabel(address: string): string {
    const block = this.memory()?.heap.find((item) => item.address === address);
    return (block?.['description'] as string) ?? '';
  }

  private stop(): void {
    this.playing.set(false);
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  ngOnDestroy(): void {
    this.stop();
  }
}
