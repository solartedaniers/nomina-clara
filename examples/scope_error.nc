# Error semantico: recargo solo existe dentro de horas_extra (uso fuera de ambito)
constante SMMLV: dinero = $1.750.905

funcion horas_extra(horas: entero, valor_hora: dinero): dinero {
    recargo: decimal = 1.25
    retornar horas * valor_hora * recargo
}

para cada empleado {
    valor_hora: dinero = salario / 240
    devengado: dinero = salario + horas_extra(extras, valor_hora) * recargo
    pagar devengado
}
