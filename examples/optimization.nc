# Valido: cadena de constantes que el optimizador pliega y propaga
constante SMMLV: dinero = $1.750.905
constante AUXILIO: dinero = $249.095
constante TOPE_AUXILIO: dinero = 2 * SMMLV
constante PRIMA: dinero = SMMLV / 2
constante DESCUENTO: decimal = 0.04 + 0.04

para cada empleado {
    devengado: dinero = salario + PRIMA
    si salario <= TOPE_AUXILIO {
        devengado = devengado + AUXILIO
    } sino {
        devengado = devengado - $10.000 * 2
    }
    pagar devengado - salario * DESCUENTO
}
