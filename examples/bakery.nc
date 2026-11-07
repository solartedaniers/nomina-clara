# Reglas de nomina 2026 - Panaderia La Esperanza
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
