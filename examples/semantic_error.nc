# Error semantico: no se puede sumar dinero con texto
constante SMMLV: dinero = $1.750.905
constante AUXILIO: dinero = $249.095

para cada empleado {
    devengado: dinero = salario
    si salario <= 2 * SMMLV {
        devengado = devengado + nombre
    }
    pagar devengado
}
