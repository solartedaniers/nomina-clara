# Error sintactico: falta la expresion despues de <=
constante SMMLV: dinero = $1.750.905

para cada empleado {
    devengado: dinero = salario
    si salario <= {
        devengado = devengado + 1000
    }
    pagar devengado
}
