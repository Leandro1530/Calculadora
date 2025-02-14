"""
Calculadora Avanzada en Python con integración de lógica en C.

Este módulo implementa una calculadora con interfaz gráfica usando tkinter y
realiza los cálculos matemáticos delegando la operación a una librería en C
mediante ctypes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import ctypes
import sys
import os
import re

# Cargar la librería de C
if sys.platform.startswith('win'):
    lib_name = os.path.join(os.path.dirname(__file__), "calculadora.dll")
else:
    lib_name = os.path.join(os.path.dirname(__file__), "libcalculadora.so")

libcalcular = ctypes.CDLL(lib_name)
libcalcular.calcular.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double]
libcalcular.calcular.restype = ctypes.c_double


class CalculadoraAvanzada:
    """
    Clase que implementa una calculadora avanzada con interfaz gráfica.
    
    La lógica de cálculo se delega a una biblioteca en C.
    """
    def __init__(self, master):
        """
        Inicializa la interfaz de usuario y las variables de estado.

        :param master: La ventana principal de tkinter.
        """
        self.master = master
        self.master.title("Calculadora Profesional (C en backend)")
        self.master.geometry("500x600")
        self.historial = []
        self.modo_cientifico = False
        self.setup_ui()

    def setup_ui(self):
        """
        Configura la interfaz: display, botones, historial y eventos de teclado.
        """
        self.master.configure(bg='#2e2e2e')
        style = ttk.Style()
        style.theme_use('clam')

        main_frame = ttk.Frame(self.master)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        self.display_var = tk.StringVar()
        display = ttk.Entry(
            main_frame, textvariable=self.display_var,
            font=('Arial', 24), justify='right'
        )
        display.grid(row=0, column=0, columnspan=5, sticky='ew', pady=5)

        # Botones numéricos
        botones_numericos = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2)
        ]

        for (texto, fila, col) in botones_numericos:
            ttk.Button(
                main_frame, text=texto,
                command=lambda t=texto: self.accion_boton(t),
                style='TButton'
            ).grid(row=fila, column=col, sticky='nsew')

        # Operaciones básicas
        operaciones_basicas = [
            ('C', 1, 3), ('⌫', 1, 4),
            ('+', 2, 3), ('-', 2, 4),
            ('*', 3, 3), ('/', 3, 4),
            ('Modo', 4, 3), ('Hist', 4, 4)
        ]

        for (texto, fila, col) in operaciones_basicas:
            ttk.Button(
                main_frame, text=texto,
                command=lambda t=texto: self.accion_boton(t),
                style='Operacion.TButton'
            ).grid(row=fila, column=col, sticky='nsew')

        # Operaciones científicas (inicialmente visibles)
        self.cientifico_frame = ttk.Frame(main_frame)
        self.cientifico_frame.grid(
            row=0, column=5, rowspan=5, sticky='nsew', padx=5
        )

        operaciones_cientificas = [
            ('sin', 0), ('cos', 1), ('tan', 2),
            ('log', 3), ('ln', 4), ('√', 5),
            ('π', 6), ('e', 7), ('^', 8),
            ('(', 9), (')', 10)
        ]

        for _, (texto, fila) in enumerate(operaciones_cientificas):
            ttk.Button(
                self.cientifico_frame, text=texto,
                command=lambda t=texto: self.accion_boton(t),
                style='Cientifico.TButton'
            ).grid(row=fila, column=0, sticky='nsew')

        for i in range(5):
            main_frame.rowconfigure(i, weight=1)
            main_frame.columnconfigure(i, weight=1)

        self.historial_text = tk.Text(
            main_frame, height=5, width=30, state='disabled'
        )
        self.historial_text.grid(
            row=5, column=0, columnspan=5, sticky='nsew', pady=5
        )

        style.configure('TButton', font=('Arial', 14),
                        background='#4a4a4a', foreground='white')
        style.configure('Operacion.TButton', background='#ff9500')
        style.configure('Cientifico.TButton', background='#3a3a3a')

        self.master.bind('<Key>', self.tecla_presionada)

    def accion_boton(self, valor):
        """
        Maneja la acción a ejecutar cuando se presiona un botón.

        :param valor: El texto del botón presionado.
        """
        current = self.display_var.get()

        if valor == '=':
            try:
                resultado = self.evaluar_expresion(current)
                self.historial.append(f"{current} = {resultado}")
                self.display_var.set(resultado)
                self.actualizar_historial()
            except (SyntaxError, ZeroDivisionError, ValueError, NameError) as e:
                messagebox.showerror("Error", f"Operación inválida: {str(e)}")
        elif valor == 'C':
            self.display_var.set('')
        elif valor == '⌫':
            self.display_var.set(current[:-1])
        elif valor == 'Modo':
            self.modo_cientifico = not self.modo_cientifico
            self.cientifico_frame.grid_configure(
                column=5 if self.modo_cientifico else 6
            )
        elif valor == 'Hist':
            self.mostrar_historial()
        elif valor in ['sin', 'cos', 'tan', 'log', 'ln', '√', 'π', 'e', 'exp']:
            if valor == '√':
                self.display_var.set("sqrt")
            elif valor in ['π', 'e']:
                const = str(math.pi) if valor == 'π' else str(math.e)
                self.display_var.set(current + const)
            else:
                self.display_var.set(current + valor)
        else:
            self.display_var.set(current + valor)

    def evaluar_expresion(self, expr):
        """
        Evalúa expresiones simples y delega la operación a la función 'calcular' de C.

        Soporta expresiones unarias (p. ej. sin45, sqrt16) y binarias (p. ej. 3+5).

        :param expr: La expresión a evaluar.
        :return: El resultado de la operación.
        :raises ValueError: Si la expresión no es reconocida o soportada.
        """
        expr = expr.strip()
        patron_unario = r'^(sin|cos|tan|sqrt|log|ln|exp)(-?\d+(\.\d+)?)$'
        match = re.fullmatch(patron_unario, expr)
        if match:
            op = match.group(1)
            num = float(match.group(2))
            if op in ['sin', 'cos', 'tan']:
                num = math.radians(num)
            return libcalcular.calcular(op.encode('utf-8'), num, 0.0)

        patron_binario = r'^(-?\d+(\.\d+)?)([\+\-\*/%\^])(-?\d+(\.\d+)?)$'
        match = re.fullmatch(patron_binario, expr)
        if match:
            num1 = float(match.group(1))
            op = match.group(3)
            num2 = float(match.group(4))
            return libcalcular.calcular(op.encode('utf-8'), num1, num2)

        raise ValueError("Expresión no reconocida o no soportada.")

    def actualizar_historial(self):
        """
        Actualiza el widget de historial con las últimas operaciones realizadas.
        """
        self.historial_text.config(state='normal')
        self.historial_text.delete(1.0, tk.END)
        self.historial_text.insert(tk.END, "\n".join(self.historial[-5:]))
        self.historial_text.config(state='disabled')

    def mostrar_historial(self):
        """
        Muestra una ventana emergente con el historial completo de operaciones.
        """
        ventana_hist = tk.Toplevel(self.master)
        ventana_hist.title("Historial Completo")
        tk.Label(ventana_hist, text="\n".join(self.historial)).pack(
            padx=20, pady=20
        )

    def tecla_presionada(self, event):
        """
        Maneja los eventos de teclado para la calculadora.

        :param event: El evento de teclado.
        """
        teclas_validas = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '+': '+', '-': '-', '*': '*', '/': '/', '.': '.',
            '^': '^', 'Return': '=', 'BackSpace': '⌫', 'Escape': 'C'
        }

        if event.keysym in teclas_validas:
            self.accion_boton(teclas_validas[event.keysym])
        elif event.char in teclas_validas:
            self.accion_boton(teclas_validas[event.char])


def main():
    """
    Función principal que inicializa la aplicación.
    """
    root = tk.Tk()
    CalculadoraAvanzada(root)
    root.mainloop()


if __name__ == "__main__":
    main()
