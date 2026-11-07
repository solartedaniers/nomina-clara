import { Employee } from '../models/compile.models';

export interface SampleProgram {
  id: string;
  labelKey: string;
  source: string;
}

// Mismos programas de la carpeta examples/ en la raíz del proyecto
export const SAMPLE_PROGRAMS: SampleProgram[] = [
  {
    id: 'bakery',
    labelKey: 'samples.bakery',
    source: `# Reglas de nomina 2026 - Panaderia La Esperanza
constante SMMLV: dinero = $1.750.905
constante AUXILIO: dinero = $249.095
constante TOPE_AUXILIO: dinero = 2 * SMMLV

funcion horas_extra(horas: entero, valor_hora: dinero): dinero {
    recargo: decimal = 1.25
    retornar horas * valor_hora * recargo
}

para cada empleado {
    valor_hora: dinero = salario / 240
    devengado: dinero = salario + horas_extra(extras, valor_hora)
    si salario <= TOPE_AUXILIO {
        devengado = devengado + AUXILIO
    }
    salud: dinero = salario * 0.04
    pension: dinero = salario * 0.04
    pagar devengado - salud - pension
}
`,
  },
  {
    id: 'lexical',
    labelKey: 'samples.lexical',
    source: `# Error lexico: el simbolo @ no pertenece al lenguaje
constante SMMLV: dinero = $1.750.905

para cada empleado {
    salud: dinero = salario @ 0.04
    pagar salario - salud
}
`,
  },
  {
    id: 'syntax',
    labelKey: 'samples.syntax',
    source: `# Error sintactico: falta la expresion despues de <=
constante SMMLV: dinero = $1.750.905

para cada empleado {
    devengado: dinero = salario
    si salario <= {
        devengado = devengado + 1000
    }
    pagar devengado
}
`,
  },
  {
    id: 'semantic',
    labelKey: 'samples.semantic',
    source: `# Error semantico: no se puede sumar dinero con texto
constante SMMLV: dinero = $1.750.905
constante AUXILIO: dinero = $249.095

para cada empleado {
    devengado: dinero = salario
    si salario <= 2 * SMMLV {
        devengado = devengado + nombre
    }
    pagar devengado
}
`,
  },
  {
    id: 'spill',
    labelKey: 'samples.spill',
    source: `# Caso con spill: 4 o mas temporales llenan los registros R0, R1 y R2
constante SMMLV: dinero = $1.750.905

para cada empleado {
    salud: dinero = salario * 0.04
    pension: dinero = salario * 0.04
    prueba: dinero = (salario - salud) * 2 + (pension + salud) * 3
    pagar prueba
}
`,
  },
];

export const DEFAULT_EMPLOYEES: Employee[] = [
  { nombre: 'Ana Ortiz', salario: 1750905, extras: 6 },
  { nombre: 'Luis Mora', salario: 4200000, extras: 0 },
  { nombre: 'Rosa Pérez', salario: 2100000, extras: 2 },
];
