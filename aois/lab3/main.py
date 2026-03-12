"""
Лабораторная работа №3: Минимизация логических функций
Запуск программы
"""

from Minimization import solve_lab3
from LogicFunction import LogicFunction


def main():
    """Основная функция"""
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №3")
    print("Минимизация логических функций")
    print("=" * 60)
    print()
    
    # Выражение из задания
    input_expr = "~((x2+~x3)*~(x1*x3))"
    
    print(f"Входное выражение: {input_expr}")
    print()
    
    # Запуск минимизации
    minimizer = solve_lab3(input_expr)
    
    print()
    print("=" * 60)
    print("Работа завершена успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()
