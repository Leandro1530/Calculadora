#include <math.h>
#include <string.h>
#include <float.h>

// Función unificada para operaciones.
// Para operaciones unarias (como "sin", "cos", etc.) se utiliza num1 y se ignora num2.
double calcular(const char* operacion, double num1, double num2) {
    if (strcmp(operacion, "+") == 0) return num1 + num2;
    if (strcmp(operacion, "-") == 0) return num1 - num2;
    if (strcmp(operacion, "*") == 0) return num1 * num2;
    if (strcmp(operacion, "/") == 0) return num2 != 0 ? num1 / num2 : DBL_MAX;
    if (strcmp(operacion, "%") == 0) return fmod(num1, num2);
    if (strcmp(operacion, "^") == 0) return pow(num1, num2);
    if (strcmp(operacion, "sqrt") == 0) return sqrt(num1);
    if (strcmp(operacion, "sin") == 0) return sin(num1);  // Se asume num1 en radianes
    if (strcmp(operacion, "cos") == 0) return cos(num1);
    if (strcmp(operacion, "tan") == 0) return tan(num1);
    if (strcmp(operacion, "log") == 0) return log10(num1);
    if (strcmp(operacion, "ln") == 0) return log(num1);
    if (strcmp(operacion, "exp") == 0) return exp(num1);
    return -INFINITY;  // Operación no reconocida
}
