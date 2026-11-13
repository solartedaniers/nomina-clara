# Valido: si / sino con ambitos propios y una funcion con 3 parametros
constante SMMLV: dinero = $1.750.905
constante AUXILIO: dinero = $249.095

funcion bono(salario_base: dinero, extras_mes: entero, tasa: decimal): dinero {
    retornar salario_base * extras_mes * tasa / 100
}

para cada empleado {
    devengado: dinero = salario + bono(salario, extras, 0.5)
    si salario <= 2 * SMMLV {
        devengado = devengado + AUXILIO
    } sino {
        extra: dinero = salario * 0.01
        devengado = devengado - extra
    }
    pagar devengado - salario * 0.08
}
