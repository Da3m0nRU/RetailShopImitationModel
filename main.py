#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Имитационная модель розничного магазина

Главный модуль для запуска приложения.
"""

import tkinter as tk
from gui import ShopSimulatorGUI


def main():
    """Функция запуска приложения"""
    root = tk.Tk()
    app = ShopSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
