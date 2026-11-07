import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { CompileRequest, CompileResponse } from '../models/compile.models';

@Injectable({ providedIn: 'root' })
export class CompilerApiService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/compile';

  compile(request: CompileRequest): Observable<CompileResponse> {
    return this.http.post<CompileResponse>(this.endpoint, request);
  }
}
