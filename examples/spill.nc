# Caso con spill: 4 o mas temporales llenan los registros R0, R1 y R2
constante SMMLV: dinero = $1.750.905

para cada empleado {
    salud: dinero = salario * 0.04
    pension: dinero = salario * 0.04
    prueba: dinero = (salario - salud) * 2 + (pension + salud) * 3
    pagar prueba
}
