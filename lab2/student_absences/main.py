#!/usr/bin/env python3
"""Точка входа приложения 'Учет пропусков студентов'."""

from controllers.main_controller import MainController

if __name__ == "__main__":
    controller = MainController()
    controller.run()