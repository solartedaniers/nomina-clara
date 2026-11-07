import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

type Dictionary = Record<string, unknown>;

@Injectable({ providedIn: 'root' })
export class I18nService {
  private readonly http = inject(HttpClient);
  private readonly dictionary = signal<Dictionary>({});

  async load(language = 'es'): Promise<void> {
    const data = await firstValueFrom(this.http.get<Dictionary>(`i18n/${language}.json`));
    this.dictionary.set(data);
  }

  translate(key: string, params?: Record<string, string | number>): string {
    const value = key
      .split('.')
      .reduce<unknown>((node, part) => (node && typeof node === 'object' ? (node as Dictionary)[part] : undefined), this.dictionary());
    const text = typeof value === 'string' ? value : key;
    if (!params) {
      return text;
    }
    return Object.entries(params).reduce((result, [name, param]) => result.replaceAll(`{{${name}}}`, String(param)), text);
  }
}
