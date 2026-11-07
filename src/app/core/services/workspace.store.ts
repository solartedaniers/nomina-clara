import { Injectable, computed, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';
import { DEFAULT_EMPLOYEES, SAMPLE_PROGRAMS } from '../data/sample-programs';
import { CompileError, CompileResponse, Employee, PhaseKey, PhaseStatus } from '../models/compile.models';
import { CompilerApiService } from './compiler-api.service';

@Injectable({ providedIn: 'root' })
export class WorkspaceStore {
  private readonly api = inject(CompilerApiService);

  readonly source = signal(SAMPLE_PROGRAMS[0].source);
  readonly employees = signal<Employee[]>(structuredClone(DEFAULT_EMPLOYEES));
  readonly response = signal<CompileResponse | null>(null);
  readonly loading = signal(false);
  readonly requestFailed = signal(false);
  readonly selectedPhase = signal<Exclude<PhaseKey, 'execution'>>('lexer');

  readonly blockingError = computed<CompileError | null>(
    () => this.response()?.errors.find((error) => !error.pending) ?? null,
  );

  readonly pendingPhases = computed(() =>
    (this.response()?.errors ?? []).filter((error) => error.pending).map((error) => error.phase),
  );

  statusOf(phase: PhaseKey): PhaseStatus | null {
    return this.response()?.status[phase] ?? null;
  }

  loadSample(sampleId: string): void {
    const sample = SAMPLE_PROGRAMS.find((program) => program.id === sampleId);
    if (sample) {
      this.source.set(sample.source);
      this.response.set(null);
    }
  }

  updateEmployee(index: number, changes: Partial<Employee>): void {
    this.employees.update((list) => list.map((employee, i) => (i === index ? { ...employee, ...changes } : employee)));
  }

  addEmployee(): void {
    this.employees.update((list) => [...list, { nombre: '', salario: 0, extras: 0 }]);
  }

  removeEmployee(index: number): void {
    this.employees.update((list) => list.filter((_, i) => i !== index));
  }

  compile(): void {
    this.loading.set(true);
    this.requestFailed.set(false);
    this.api
      .compile({ source: this.source(), employees: this.employees() })
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (response) => {
          this.response.set(response);
          this.selectedPhase.set(this.firstInterestingPhase(response));
        },
        error: () => this.requestFailed.set(true),
      });
  }

  private firstInterestingPhase(response: CompileResponse): Exclude<PhaseKey, 'execution'> {
    const order: Exclude<PhaseKey, 'execution'>[] = ['lexer', 'parser', 'semantic', 'ir', 'memory', 'optimizer', 'codegen'];
    return order.find((phase) => response.status[phase] === 'failed') ?? this.selectedPhase();
  }
}
