import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import numpy as np

from simulation import ShopSimulation
from visualization import SimulationVisualizer


class ShopSimulatorGUI:
    """Графический интерфейс для имитационной модели магазина"""

    def __init__(self, root):
        self.root = root
        self.root.title("Имитационная модель магазина")
        self.root.geometry("1000x650")
        self.root.minsize(800, 600)

        # Создание вкладок
        self.tab_control = ttk.Notebook(root)

        self.tab_simulation = ttk.Frame(self.tab_control)
        self.tab_experiment = ttk.Frame(self.tab_control)
        self.tab_results = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_simulation, text="Симуляция")
        self.tab_control.add(self.tab_experiment, text="Эксперимент")
        self.tab_control.add(self.tab_results, text="Результаты")

        self.tab_control.pack(expand=1, fill="both")

        # Инициализация интерфейса на вкладках
        self._init_simulation_tab()
        self._init_experiment_tab()
        self._init_results_tab()

        # Результаты симуляции
        self.simulation_results = None
        self.experiment_results = []
        self.experiment_param_values = []

        # Флаги состояния симуляции
        self.is_simulating = False

        # Текущий отображаемый график
        self.current_canvas = None

    def _init_simulation_tab(self):
        """Инициализация вкладки настройки и запуска симуляции"""
        # Создаем фрейм с параметрами
        params_frame = ttk.LabelFrame(
            self.tab_simulation, text="Параметры симуляции")
        params_frame.pack(padx=10, pady=10, fill="x")

        # Создаем сетку для элементов управления
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(padx=10, pady=10, fill="x")

        # Время симуляции
        ttk.Label(params_grid, text="Время симуляции (мин):").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.simulation_time_var = tk.StringVar(value="480")
        ttk.Entry(params_grid, textvariable=self.simulation_time_var,
                  width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Seed для воспроизводимости
        ttk.Label(params_grid, text="Seed:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5)
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(params_grid, textvariable=self.seed_var, width=10).grid(
            row=0, column=3, padx=5, pady=5, sticky="w")

        # Параметры покупателей
        ttk.Label(params_grid, text="Среднее время между прибытиями (мин):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.arrival_mean_var = tk.StringVar(value="5")
        ttk.Entry(params_grid, textvariable=self.arrival_mean_var, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")

        # Параметры выбора товаров
        shopping_frame = ttk.LabelFrame(
            params_frame, text="Параметры времени выбора товаров")
        shopping_frame.pack(padx=10, pady=5, fill="x")

        # Распределение времени выбора товаров
        ttk.Label(shopping_frame, text="Распределение:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.shopping_dist_var = tk.StringVar(value="Нормальное")
        shopping_dist_combo = ttk.Combobox(shopping_frame, textvariable=self.shopping_dist_var,
                                           values=["Нормальное", "Равномерное", "Экспоненциальное"], width=20, state="readonly")
        shopping_dist_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Среднее время выбора товаров
        ttk.Label(shopping_frame, text="Среднее время (мин):").grid(
            row=0, column=2, sticky="w", padx=5, pady=5)
        self.shopping_mean_var = tk.StringVar(value="15")
        ttk.Entry(shopping_frame, textvariable=self.shopping_mean_var, width=10).grid(
            row=0, column=3, padx=5, pady=5, sticky="w")

        # Стандартное отклонение времени выбора товаров
        ttk.Label(shopping_frame, text="Стандартное отклонение (мин):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.shopping_std_var = tk.StringVar(value="5")
        ttk.Entry(shopping_frame, textvariable=self.shopping_std_var, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")

        # Мин. и макс. время выбора товаров
        ttk.Label(shopping_frame, text="Минимум (мин):").grid(
            row=1, column=2, sticky="w", padx=5, pady=5)
        self.shopping_min_var = tk.StringVar(value="5")
        ttk.Entry(shopping_frame, textvariable=self.shopping_min_var, width=10).grid(
            row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(shopping_frame, text="Максимум (мин):").grid(
            row=1, column=4, sticky="w", padx=5, pady=5)
        self.shopping_max_var = tk.StringVar(value="30")
        ttk.Entry(shopping_frame, textvariable=self.shopping_max_var, width=10).grid(
            row=1, column=5, padx=5, pady=5, sticky="w")

        # Параметры касс
        cashdesk_frame = ttk.LabelFrame(params_frame, text="Параметры касс")
        cashdesk_frame.pack(padx=10, pady=5, fill="x")

        # Количество касс
        ttk.Label(cashdesk_frame, text="Количество касс:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.cash_desks_var = tk.StringVar(value="3")
        ttk.Entry(cashdesk_frame, textvariable=self.cash_desks_var, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky="w")

        # Распределение времени обслуживания
        ttk.Label(cashdesk_frame, text="Распределение времени обслуживания:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5)
        self.service_dist_var = tk.StringVar(value="Экспоненциальное")
        service_dist_combo = ttk.Combobox(cashdesk_frame, textvariable=self.service_dist_var,
                                          values=["Экспоненциальное", "Нормальное"], width=20, state="readonly")
        service_dist_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Среднее время обслуживания
        ttk.Label(cashdesk_frame, text="Среднее время обслуживания (мин):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.service_mean_var = tk.StringVar(value="3")
        ttk.Entry(cashdesk_frame, textvariable=self.service_mean_var, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")

        # Стандартное отклонение времени обслуживания
        ttk.Label(cashdesk_frame, text="Стандартное отклонение (мин):").grid(
            row=1, column=2, sticky="w", padx=5, pady=5)
        self.service_std_var = tk.StringVar(value="1")
        ttk.Entry(cashdesk_frame, textvariable=self.service_std_var, width=10).grid(
            row=1, column=3, padx=5, pady=5, sticky="w")

        # Кнопки управления
        control_frame = ttk.Frame(self.tab_simulation)
        control_frame.pack(padx=10, pady=10, fill="x")

        self.run_button = ttk.Button(
            control_frame, text="Запустить симуляцию", command=self.run_simulation)
        self.run_button.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Просмотреть результаты",
                   command=lambda: self.tab_control.select(self.tab_results)).pack(side="left", padx=5)

    def _init_experiment_tab(self):
        """Инициализация вкладки настройки и запуска экспериментов"""
        experiment_frame = ttk.LabelFrame(
            self.tab_experiment, text="Настройка эксперимента")
        experiment_frame.pack(padx=10, pady=10, fill="x")

        # Выбор параметра для эксперимента
        ttk.Label(experiment_frame, text="Изменяемый параметр:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.experiment_param_var = tk.StringVar(value="Количество касс")
        param_combo = ttk.Combobox(experiment_frame, textvariable=self.experiment_param_var,
                                   values=["Количество касс", "Интервал прибытия покупателей",
                                           "Среднее время выбора товаров", "Среднее время обслуживания"],
                                   width=25, state="readonly")
        param_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Диапазон значений параметра
        ttk.Label(experiment_frame, text="Начальное значение:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.param_start_var = tk.StringVar(value="1")
        ttk.Entry(experiment_frame, textvariable=self.param_start_var, width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(experiment_frame, text="Конечное значение:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        self.param_end_var = tk.StringVar(value="5")
        ttk.Entry(experiment_frame, textvariable=self.param_end_var, width=10).grid(
            row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(experiment_frame, text="Шаг:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        self.param_step_var = tk.StringVar(value="1")
        ttk.Entry(experiment_frame, textvariable=self.param_step_var, width=10).grid(
            row=3, column=1, padx=5, pady=5, sticky="w")

        # Выбор метрики для анализа
        ttk.Label(experiment_frame, text="Анализируемая метрика:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5)
        self.experiment_metric_var = tk.StringVar(
            value="Среднее время ожидания")
        metric_combo = ttk.Combobox(experiment_frame, textvariable=self.experiment_metric_var,
                                    values=["Среднее время ожидания", "Среднее время в магазине",
                                            "Средняя длина очереди", "Средняя загрузка касс"],
                                    width=25, state="readonly")
        metric_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Кнопка запуска эксперимента
        self.run_experiment_button = ttk.Button(experiment_frame, text="Запустить эксперимент",
                                                command=self.run_experiment)
        self.run_experiment_button.grid(
            row=4, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        # Фрейм для графика эксперимента
        self.experiment_plot_frame = ttk.LabelFrame(
            self.tab_experiment, text="Результаты эксперимента")
        self.experiment_plot_frame.pack(
            padx=10, pady=10, fill="both", expand=True)

    def _init_results_tab(self):
        """Инициализация вкладки отображения результатов"""
        # Создаем область для отображения текстовых результатов
        stats_frame = ttk.LabelFrame(
            self.tab_results, text="Основные показатели")
        stats_frame.pack(padx=10, pady=10, fill="x")

        # Область для вывода статистики
        self.stats_text = tk.Text(stats_frame, height=10, width=80)
        self.stats_text.pack(padx=10, pady=10, fill="x")

        # Добавляем возможность копирования текста
        # Разрешаем редактирование для копирования
        self.stats_text.configure(state="normal")

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.stats_text.config(yscrollcommand=scrollbar.set)

        # Добавляем контекстное меню для копирования
        self.context_menu = tk.Menu(self.stats_text, tearoff=0)
        self.context_menu.add_command(
            label="Копировать", command=self._copy_text)

        # Привязываем контекстное меню к правой кнопке мыши
        self.stats_text.bind("<Button-3>", self._show_context_menu)

        # Привязываем стандартные сочетания клавиш для копирования
        self.stats_text.bind("<Control-c>", self._copy_text)

        # Создаем фрейм для графиков
        self.plots_frame = ttk.LabelFrame(self.tab_results, text="Графики")
        self.plots_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Кнопки для выбора графиков
        plots_control = ttk.Frame(self.plots_frame)
        plots_control.pack(padx=10, pady=5, fill="x")

        ttk.Button(plots_control, text="Сводная панель",
                   command=lambda: self.show_plot('dashboard')).pack(side="left", padx=5)
        ttk.Button(plots_control, text="Длина очереди",
                   command=lambda: self.show_plot('queue_length')).pack(side="left", padx=5)
        ttk.Button(plots_control, text="Время ожидания",
                   command=lambda: self.show_plot('waiting_time')).pack(side="left", padx=5)
        ttk.Button(plots_control, text="Время в магазине",
                   command=lambda: self.show_plot('time_in_shop')).pack(side="left", padx=5)
        ttk.Button(plots_control, text="Загрузка касс",
                   command=lambda: self.show_plot('cash_desk_utilization')).pack(side="left", padx=5)

        # Область для вывода графиков
        self.canvas_frame = ttk.Frame(self.plots_frame)
        self.canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)

    def _get_simulation_params(self):
        """Получение параметров симуляции из интерфейса"""
        try:
            # Преобразование русских названий в английские для модели
            shopping_dist_map = {
                "Нормальное": "normal",
                "Равномерное": "uniform",
                "Экспоненциальное": "exponential"
            }

            service_dist_map = {
                "Экспоненциальное": "exponential",
                "Нормальное": "normal"
            }

            params = {
                'seed': int(self.seed_var.get()),
                'simulation_time': float(self.simulation_time_var.get()),
                'customer_arrival_mean': float(self.arrival_mean_var.get()),
                'shopping_time_dist': shopping_dist_map[self.shopping_dist_var.get()],
                'shopping_time_mean': float(self.shopping_mean_var.get()),
                'shopping_time_std': float(self.shopping_std_var.get()),
                'shopping_time_min': float(self.shopping_min_var.get()),
                'shopping_time_max': float(self.shopping_max_var.get()),
                'num_cash_desks': int(self.cash_desks_var.get()),
                'service_time_dist': service_dist_map[self.service_dist_var.get()],
                'service_time_mean': float(self.service_mean_var.get()),
                'service_time_std': float(self.service_std_var.get())
            }
            return params
        except ValueError as e:
            messagebox.showerror(
                "Ошибка ввода", f"Неверный формат входных данных: {str(e)}")
            return None

    def run_simulation(self):
        """Запуск симуляции на основе параметров из интерфейса"""
        if self.is_simulating:
            return

        params = self._get_simulation_params()
        if not params:
            return

        # Обновление статуса
        self.is_simulating = True
        self.run_button.config(state="disabled")

        # Запуск симуляции в отдельном потоке
        threading.Thread(target=self._simulation_thread,
                         args=(params,), daemon=True).start()

    def _simulation_thread(self, params):
        """Поток симуляции для запуска без блокировки GUI"""
        try:
            # Создание и запуск модели
            simulation = ShopSimulation(params)
            results = simulation.run_simulation()

            # Сохранение результатов
            self.simulation_results = results

            # Обновление интерфейса с результатами
            self.root.after(0, self._update_simulation_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка симуляции", str(e)))
        finally:
            # Обновление статуса
            self.root.after(0, lambda: self.run_button.config(state="normal"))
            self.is_simulating = False

    def _generate_conclusions(self, results):
        """Генерирует аналитические выводы на основе результатов симуляции"""
        conclusions = []

        # Анализ загрузки касс
        avg_utilization = results.get('avg_cash_desk_utilization', 0)
        if avg_utilization < 0.3:
            conclusions.append(
                "Низкая загрузка кассовых узлов (менее 30%). Возможно, стоит уменьшить количество касс.")
        elif avg_utilization > 0.85:
            conclusions.append(
                "Высокая загрузка кассовых узлов (более 85%). Рекомендуется увеличить количество касс.")
        else:
            conclusions.append("Оптимальная загрузка кассовых узлов.")

        # Анализ очередей
        avg_queue_length = results.get('avg_queue_length', 0)
        if avg_queue_length > 3:
            conclusions.append(
                f"Средняя длина очереди ({avg_queue_length:.1f} чел.) превышает рекомендуемую. Рекомендуется увеличить количество касс.")

        # Анализ времени ожидания
        avg_waiting_time = results.get('avg_waiting_time', 0)
        if avg_waiting_time > 5:
            conclusions.append(
                f"Среднее время ожидания ({avg_waiting_time:.1f} мин) превышает комфортное для покупателей. Рекомендуется оптимизировать обслуживание.")

        # Анализ соотношения обслуженных и прибывших покупателей
        arrived = results.get('total_customers_arrived', 0)
        served = results.get('total_customers_served', 0)
        if arrived > 0:
            service_rate = served / arrived
            if service_rate < 0.95:
                conclusions.append(
                    f"Обслужено только {service_rate:.1%} прибывших покупателей. Возможно, время симуляции недостаточно для корректной оценки.")

        # Если выводов нет, добавляем общий вывод
        if not conclusions:
            conclusions.append("Система работает в оптимальном режиме.")

        return conclusions

    def _update_simulation_results(self):
        """Обновление интерфейса с результатами симуляции"""
        if not self.simulation_results:
            return

        # Преобразование типов распределений для отображения
        dist_names = {
            "normal": "Нормальное",
            "uniform": "Равномерное",
            "exponential": "Экспоненциальное"
        }

        # Получаем имена распределений
        shopping_dist = dist_names.get(
            self.shopping_dist_var.get(), self.shopping_dist_var.get())
        service_dist = dist_names.get(
            self.service_dist_var.get(), self.service_dist_var.get())

        # Отображение статистики в текстовом поле
        self.stats_text.delete(1.0, tk.END)

        stats_text = f"""Результаты симуляции:
        
Параметры модели:
- Время симуляции: {self.simulation_time_var.get()} мин
- Интервал прибытия покупателей: {self.arrival_mean_var.get()} мин (экспоненциальное распределение)
- Распределение времени выбора товаров: {shopping_dist}
- Распределение времени обслуживания: {service_dist}
- Количество касс: {self.cash_desks_var.get()}

Результаты:
- Общее количество прибывших покупателей: {self.simulation_results['total_customers_arrived']}
- Общее количество обслуженных покупателей: {self.simulation_results['total_customers_served']}

- Среднее время нахождения в магазине: {self.simulation_results['avg_time_in_shop']:.2f} мин
- Максимальное время нахождения в магазине: {self.simulation_results['max_time_in_shop']:.2f} мин

- Среднее время ожидания в очереди: {self.simulation_results['avg_waiting_time']:.2f} мин
- Максимальное время ожидания в очереди: {self.simulation_results['max_waiting_time']:.2f} мин

- Средняя длина очереди: {self.simulation_results['avg_queue_length']:.2f} чел.
- Максимальная длина очереди: {self.simulation_results['max_queue_length']:.0f} чел.

- Средняя загрузка кассовых узлов: {self.simulation_results['avg_cash_desk_utilization']:.1%}

Выводы:"""
        self.stats_text.insert(tk.END, stats_text)

        # Добавление выводов
        conclusions = self._generate_conclusions(self.simulation_results)
        for conclusion in conclusions:
            self.stats_text.insert(tk.END, f"\n- {conclusion}")

        # Убеждаемся, что текстовое поле доступно для выделения и копирования
        self.stats_text.configure(state="normal")

        # Отображение сводного графика
        self.show_plot('dashboard')

        # Переключение на вкладку результатов
        self.tab_control.select(self.tab_results)

    def show_plot(self, plot_type):
        """Отображение графика заданного типа"""
        if not self.simulation_results:
            messagebox.showinfo("Информация", "Сначала запустите симуляцию")
            return

        # Очистка фрейма для графика
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Создание визуализатора
        visualizer = SimulationVisualizer(self.simulation_results)

        # Выбор и отображение графика
        fig = None
        if plot_type == 'dashboard':
            fig = visualizer.create_summary_dashboard()
        elif plot_type == 'queue_length':
            fig = visualizer.plot_queue_length_over_time()
        elif plot_type == 'waiting_time':
            fig = visualizer.plot_waiting_time_histogram()
        elif plot_type == 'time_in_shop':
            fig = visualizer.plot_time_in_shop_histogram()
        elif plot_type == 'cash_desk_utilization':
            fig = visualizer.plot_cash_desk_utilization()

        if fig:
            # Создание канваса для отображения
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.current_canvas = canvas
        else:
            label = ttk.Label(self.canvas_frame,
                              text="Нет данных для отображения графика")
            label.pack(padx=20, pady=20)

    def run_experiment(self):
        """Запуск серии экспериментов с изменением параметра"""
        if self.is_simulating:
            return

        # Получение базовых параметров
        base_params = self._get_simulation_params()
        if not base_params:
            return

        try:
            # Настройки эксперимента
            param_name = self.experiment_param_var.get()
            param_start = float(self.param_start_var.get())
            param_end = float(self.param_end_var.get())
            param_step = float(self.param_step_var.get())
            metric_name = self.experiment_metric_var.get()

            # Проверка корректности значений
            if param_start > param_end or param_step <= 0:
                messagebox.showerror(
                    "Ошибка", "Некорректные параметры эксперимента")
                return

            # Для количества касс обеспечиваем целочисленные значения
            if param_name == "Количество касс":
                # Округляем до целых и преобразуем в int
                param_start = int(param_start)
                param_end = int(param_end)
                param_step = int(max(1, param_step))  # Минимальный шаг 1
                param_values = np.array(
                    range(param_start, param_end + 1, param_step))
            else:
                # Создание списка значений параметра для других типов
                param_values = np.arange(
                    param_start, param_end + param_step/2, param_step)

            # Обновление статуса
            self.is_simulating = True
            self.run_experiment_button.config(state="disabled")

            # Запуск эксперимента в отдельном потоке
            threading.Thread(target=self._experiment_thread,
                             args=(base_params, param_name,
                                   param_values, metric_name),
                             daemon=True).start()

        except ValueError as e:
            messagebox.showerror(
                "Ошибка ввода", f"Неверный формат входных данных: {str(e)}")

    def _experiment_thread(self, base_params, param_name, param_values, metric_name):
        """Поток для запуска серии экспериментов"""
        try:
            # Словарь для преобразования русских названий в английские
            param_name_map = {
                "Количество касс": "num_cash_desks",
                "Интервал прибытия покупателей": "customer_arrival_mean",
                "Среднее время выбора товаров": "shopping_time_mean",
                "Среднее время обслуживания": "service_time_mean"
            }

            metric_name_map = {
                "Среднее время ожидания": "avg_waiting_time",
                "Среднее время в магазине": "avg_time_in_shop",
                "Средняя длина очереди": "avg_queue_length",
                "Средняя загрузка касс": "avg_cash_desk_utilization"
            }

            # Преобразование названий для модели
            param_name_eng = param_name_map[param_name]
            metric_name_eng = metric_name_map[metric_name]

            # Список для хранения результатов
            results = []

            # Преобразуем param_values в обычный список для безопасной передачи
            param_values_list = param_values.tolist() if hasattr(
                param_values, 'tolist') else list(param_values)

            # Запуск симуляций для каждого значения параметра
            for value in param_values:
                # Копирование базовых параметров и изменение нужного
                params = base_params.copy()

                # Преобразуем значение в правильный тип данных для параметра
                if param_name_eng == "num_cash_desks":
                    params[param_name_eng] = int(value)
                else:
                    params[param_name_eng] = float(value)

                # Создание и запуск модели
                simulation = ShopSimulation(params)
                result = simulation.run_simulation()
                results.append(result)

            # Сохранение результатов
            self.experiment_results = results
            self.experiment_param_values = param_values_list

            # Обновление интерфейса с результатами - передаем английские имена для обработки
            self.root.after(0, lambda: self._show_experiment_results(
                param_name_eng, param_values_list, metric_name_eng))
        except Exception as e:
            import traceback
            error_msg = f"Ошибка эксперимента: {str(e)}\n{traceback.format_exc()}"
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка эксперимента", error_msg))
        finally:
            # Обновление статуса
            self.root.after(
                0, lambda: self.run_experiment_button.config(state="normal"))
            self.is_simulating = False

    def _generate_experiment_conclusions(self, param_name, param_values, metric_name, experiment_results):
        """Генерирует выводы по результатам серии экспериментов"""
        if not experiment_results or len(param_values) == 0:
            return ["Недостаточно данных для формирования выводов."]

        conclusions = []

        # Получаем значения метрики для всех экспериментов
        metric_values = [result.get(metric_name, 0)
                         for result in experiment_results]

        # Находим оптимальное значение параметра
        if metric_name in ["avg_waiting_time", "avg_time_in_shop", "avg_queue_length"]:
            # Для этих метрик ищем минимум
            best_idx = np.argmin(metric_values)
            best_value = param_values[best_idx]
            best_metric = metric_values[best_idx]

            if param_name == "num_cash_desks":
                conclusions.append(
                    f"Оптимальное количество касс: {int(best_value)} (при этом {self._get_metric_name_ru(metric_name)}: {best_metric:.2f})")

                # Анализ эффективности добавления касс
                if len(param_values) > 1:
                    improvements = []
                    for i in range(1, len(param_values)):
                        if metric_values[i] < metric_values[i-1]:
                            improvement = (
                                metric_values[i-1] - metric_values[i]) / metric_values[i-1]
                            improvements.append((param_values[i], improvement))

                    if improvements:
                        best_improvement = max(
                            improvements, key=lambda x: x[1])
                        if best_improvement[1] > 0.2:  # Если улучшение более 20%
                            conclusions.append(
                                f"Наибольший эффект дает увеличение количества касс до {int(best_improvement[0])} (улучшение на {best_improvement[1]:.1%})")

            elif param_name == "customer_arrival_mean":
                conclusions.append(
                    f"При интервале прибытия покупателей {float(best_value):.1f} мин достигается минимальное {self._get_metric_name_ru(metric_name)}: {best_metric:.2f}")

                # Анализ критической нагрузки
                critical_idx = None
                for i in range(len(param_values)-1):
                    if param_values[i+1] > param_values[i] and metric_values[i+1] < metric_values[i] * 0.5:
                        critical_idx = i
                        break

                if critical_idx is not None:
                    conclusions.append(
                        f"Критический интервал прибытия: {float(param_values[critical_idx]):.1f} мин, при его уменьшении резко возрастает {self._get_metric_name_ru(metric_name)}")

            else:  # Для остальных параметров
                conclusions.append(
                    f"Оптимальное значение параметра '{self._get_param_name_ru(param_name)}': {float(best_value):.1f}")

        elif metric_name == "avg_cash_desk_utilization":
            # Для загрузки касс ищем оптимальное значение (не слишком низкое, не слишком высокое)
            optimal_idx = None
            for i, value in enumerate(metric_values):
                if 0.7 <= value <= 0.85:
                    optimal_idx = i
                    break

            if optimal_idx is not None:
                optimal_value = param_values[optimal_idx]
                if param_name == "num_cash_desks":
                    conclusions.append(
                        f"Оптимальная загрузка касс ({metric_values[optimal_idx]:.1%}) достигается при количестве касс: {int(optimal_value)}")
                else:
                    conclusions.append(
                        f"Оптимальная загрузка касс ({metric_values[optimal_idx]:.1%}) достигается при значении параметра '{self._get_param_name_ru(param_name)}': {float(optimal_value):.1f}")
            else:
                # Если оптимальное значение не найдено, ищем ближайшее к 0.75
                best_idx = np.argmin(np.abs(np.array(metric_values) - 0.75))
                best_value = param_values[best_idx]
                if param_name == "num_cash_desks":
                    conclusions.append(
                        f"Ближайшая к оптимальной загрузка касс ({metric_values[best_idx]:.1%}) достигается при количестве касс: {int(best_value)}")
                else:
                    conclusions.append(
                        f"Ближайшая к оптимальной загрузка касс ({metric_values[best_idx]:.1%}) достигается при значении параметра '{self._get_param_name_ru(param_name)}': {float(best_value):.1f}")

        # Общий тренд
        if len(param_values) > 2:
            is_decreasing = True
            is_increasing = True

            for i in range(1, len(metric_values)):
                if metric_values[i] > metric_values[i-1]:
                    is_decreasing = False
                if metric_values[i] < metric_values[i-1]:
                    is_increasing = False

            if is_decreasing:
                conclusions.append(
                    f"Наблюдается устойчивое снижение {self._get_metric_name_ru(metric_name)} при увеличении параметра '{self._get_param_name_ru(param_name)}'")
            elif is_increasing:
                conclusions.append(
                    f"Наблюдается устойчивый рост {self._get_metric_name_ru(metric_name)} при увеличении параметра '{self._get_param_name_ru(param_name)}'")

        return conclusions

    def _get_param_name_ru(self, param_name):
        """Возвращает русское название параметра"""
        param_labels = {
            "num_cash_desks": "Количество касс",
            "customer_arrival_mean": "Интервал прибытия покупателей",
            "shopping_time_mean": "Среднее время выбора товаров",
            "service_time_mean": "Среднее время обслуживания"
        }
        return param_labels.get(param_name, param_name)

    def _get_metric_name_ru(self, metric_name):
        """Возвращает русское название метрики"""
        metric_labels = {
            "avg_waiting_time": "среднее время ожидания",
            "avg_time_in_shop": "среднее время в магазине",
            "avg_queue_length": "средняя длина очереди",
            "avg_cash_desk_utilization": "средняя загрузка касс"
        }
        return metric_labels.get(metric_name, metric_name)

    def _show_experiment_results(self, param_name, param_values, metric_name):
        """Отображение результатов эксперимента"""
        if not self.experiment_results:
            return

        # Очистка фрейма для графика
        for widget in self.experiment_plot_frame.winfo_children():
            widget.destroy()

        # Создаем фрейм для результатов
        results_frame = ttk.Frame(self.experiment_plot_frame)
        results_frame.pack(fill="both", expand=True)

        # Фрейм для графика
        plot_frame = ttk.Frame(results_frame)
        plot_frame.pack(fill="both", expand=True, side="left", padx=5, pady=5)

        # Фрейм для выводов
        conclusions_frame = ttk.LabelFrame(
            results_frame, text="Выводы по эксперименту")
        conclusions_frame.pack(fill="y", side="right", padx=5,
                               pady=5, ipadx=5, ipady=5, anchor="ne", expand=False)

        # Создание визуализатора и построение графика эксперимента
        visualizer = SimulationVisualizer({})
        fig = visualizer.plot_comparative_experiment(
            self.experiment_results, param_name, param_values, metric_name)

        if fig:
            # Создание канваса для отображения графика
            canvas = FigureCanvasTkAgg(fig, plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Генерация и отображение выводов
            conclusions = self._generate_experiment_conclusions(
                param_name, param_values, metric_name, self.experiment_results)

            # Создаем текстовое поле для выводов с возможностью копирования
            conclusions_text = tk.Text(
                conclusions_frame, width=40, height=15, wrap=tk.WORD)
            conclusions_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Добавляем скроллбар
            scrollbar = ttk.Scrollbar(
                conclusions_frame, command=conclusions_text.yview)
            scrollbar.pack(side="right", fill="y")
            conclusions_text.config(yscrollcommand=scrollbar.set)

            # Вставляем выводы
            for conclusion in conclusions:
                conclusions_text.insert(tk.END, f"• {conclusion}\n\n")

            # Делаем текст доступным для копирования, но не для редактирования
            conclusions_text.configure(state="normal")

            # Добавляем контекстное меню для копирования
            conclusions_menu = tk.Menu(conclusions_text, tearoff=0)
            conclusions_menu.add_command(
                label="Копировать", command=lambda: self._copy_conclusions_text(conclusions_text))

            # Привязываем контекстное меню к правой кнопке мыши
            conclusions_text.bind(
                "<Button-3>", lambda event: self._show_conclusions_menu(event, conclusions_menu))

            # Привязываем стандартные сочетания клавиш для копирования
            conclusions_text.bind(
                "<Control-c>", lambda event: self._copy_conclusions_text(conclusions_text, event))
        else:
            label = ttk.Label(plot_frame, text="Нет данных для отображения")
            label.pack(padx=20, pady=20)

    def _copy_conclusions_text(self, text_widget, event=None):
        """Копирование выделенного текста из выводов по экспериментам"""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                return "break"
        except tk.TclError:
            # Нет выделенного текста
            pass
        return None

    def _show_conclusions_menu(self, event, menu):
        """Показывает контекстное меню для выводов по экспериментам"""
        try:
            event.widget.tag_add(tk.SEL, "insert", "insert+1c")
        except:
            pass
        menu.post(event.x_root, event.y_root)
        return "break"

    def _copy_text(self, event=None):
        """Копирование выделенного текста"""
        try:
            selected_text = self.stats_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                return "break"  # Предотвращает стандартную обработку события
        except tk.TclError:
            # Нет выделенного текста
            pass
        return None

    def _show_context_menu(self, event):
        """Показывает контекстное меню при нажатии правой кнопки мыши"""
        try:
            self.stats_text.tag_add(tk.SEL, "insert", "insert+1c")
        except:
            pass
        self.context_menu.post(event.x_root, event.y_root)
        return "break"

# Запуск приложения


def main():
    root = tk.Tk()
    app = ShopSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
