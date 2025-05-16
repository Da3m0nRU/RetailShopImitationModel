import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class SimulationVisualizer:
    """Класс для визуализации результатов симуляции магазина"""

    def __init__(self, results):
        """
        Инициализация визуализатора с результатами симуляции

        Args:
            results (dict): Словарь с результатами симуляции
        """
        self.results = results
        # Настройка стиля графиков
        sns.set(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 12

    def plot_queue_length_over_time(self):
        """Построение графика изменения длины очереди во времени"""
        if not self.results.get('queue_length_time_series'):
            return None

        # Преобразование данных
        times, lengths = zip(*sorted(self.results['queue_length_time_series']))

        fig, ax = plt.subplots()
        ax.plot(times, lengths, linewidth=1.5)
        ax.set_title('Изменение длины очереди во времени')
        ax.set_xlabel('Время (мин)')
        ax.set_ylabel('Длина очереди (чел.)')
        ax.grid(True)

        # Добавление средней длины очереди
        avg_queue_length = self.results.get('avg_queue_length', 0)
        ax.axhline(y=avg_queue_length, color='r', linestyle='--',
                   label=f'Средняя длина: {avg_queue_length:.2f}')
        ax.legend()

        return fig

    def plot_waiting_time_histogram(self):
        """Построение гистограммы времени ожидания в очереди"""
        waiting_times = self.results.get('waiting_time_distribution', [])
        if not waiting_times:
            return None

        fig, ax = plt.subplots()
        sns.histplot(waiting_times, kde=True, ax=ax)
        ax.set_title('Распределение времени ожидания в очереди')
        ax.set_xlabel('Время ожидания (мин)')
        ax.set_ylabel('Количество покупателей')

        # Добавление среднего времени ожидания
        avg_waiting_time = self.results.get('avg_waiting_time', 0)
        ax.axvline(x=avg_waiting_time, color='r', linestyle='--',
                   label=f'Среднее время: {avg_waiting_time:.2f} мин')
        ax.legend()

        return fig

    def plot_time_in_shop_histogram(self):
        """Построение гистограммы времени нахождения в магазине"""
        times_in_shop = self.results.get('time_in_shop_distribution', [])
        if not times_in_shop:
            return None

        fig, ax = plt.subplots()
        sns.histplot(times_in_shop, kde=True, ax=ax)
        ax.set_title('Распределение времени нахождения в магазине')
        ax.set_xlabel('Время (мин)')
        ax.set_ylabel('Количество покупателей')

        # Добавление среднего времени
        avg_time = self.results.get('avg_time_in_shop', 0)
        ax.axvline(x=avg_time, color='r', linestyle='--',
                   label=f'Среднее время: {avg_time:.2f} мин')
        ax.legend()

        return fig

    def plot_cash_desk_utilization(self):
        """Построение диаграммы коэффициентов загрузки касс"""
        utilization = self.results.get('cash_desk_utilization', {})
        if not utilization:
            return None

        # Преобразование данных для построения - теперь сортируем по номеру кассы
        desk_ids = sorted(utilization.keys())
        utilization_values = [utilization[desk_id] for desk_id in desk_ids]

        # Создаем понятные метки для касс (нумерация с 1)
        desk_labels = [f'{desk_id + 1}' for desk_id in desk_ids]

        fig, ax = plt.subplots()
        bars = ax.bar(desk_labels, utilization_values,
                      color=sns.color_palette("viridis", len(utilization)))

        # Добавление процентов над столбцами
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.1%}', ha='center', va='bottom')

        ax.set_title('Коэффициент загрузки кассовых узлов')
        ax.set_xlabel('Номер кассы')
        ax.set_ylabel('Коэффициент загрузки')
        ax.set_ylim(0, 1.1)  # от 0 до 110% для отображения текста

        # Форматирование оси Y в процентах
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

        # Добавление среднего значения
        avg_utilization = self.results.get('avg_cash_desk_utilization', 0)
        ax.axhline(y=avg_utilization, color='r', linestyle='--',
                   label=f'Средняя загрузка: {avg_utilization:.1%}')
        ax.legend()

        return fig

    def plot_comparative_experiment(self, experiment_results, param_name, param_values, metric_name):
        """Построение графика сравнительного эксперимента

        Args:
            experiment_results: список словарей с результатами для разных значений параметра
            param_name: имя изменяемого параметра
            param_values: список значений параметра
            metric_name: имя метрики для сравнения
        """
        if len(experiment_results) == 0 or len(param_values) == 0:
            return None

        # Извлечение значений метрики для всех экспериментов
        metric_values = [result.get(metric_name, 0)
                         for result in experiment_results]

        # Преобразуем param_values в список чисел для корректного отображения на графике
        param_values_numeric = [float(val) for val in param_values]

        # Словари для отображения названий на русском языке
        param_labels = {
            "num_cash_desks": "Количество касс",
            "customer_arrival_mean": "Интервал прибытия покупателей (мин)",
            "shopping_time_mean": "Среднее время выбора товаров (мин)",
            "service_time_mean": "Среднее время обслуживания (мин)"
        }

        metric_labels = {
            "avg_waiting_time": "Среднее время ожидания (мин)",
            "avg_time_in_shop": "Среднее время в магазине (мин)",
            "avg_queue_length": "Средняя длина очереди (чел.)",
            "avg_cash_desk_utilization": "Средняя загрузка касс"
        }

        # Получение русских названий или использование оригинальных, если перевод не найден
        param_label = param_labels.get(param_name, param_name)
        metric_label = metric_labels.get(metric_name, metric_name)

        fig, ax = plt.subplots()
        ax.plot(param_values_numeric, metric_values, 'o-', linewidth=2)
        ax.set_title(
            f'Зависимость {metric_label} от параметра\n"{param_label}"')
        ax.set_xlabel(param_label)
        ax.set_ylabel(metric_label)
        ax.grid(True)

        # Если параметр - количество касс, устанавливаем целочисленные метки на оси X
        if param_name == "num_cash_desks":
            ax.set_xticks(param_values_numeric)
            ax.set_xticklabels([int(val) for val in param_values_numeric])

        # Если метрика - загрузка касс, отображаем в процентах
        if metric_name == "avg_cash_desk_utilization":
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

        return fig

    def create_summary_dashboard(self):
        """Создание панели с основными показателями симуляции"""
        # Создание фигуры с 4 графиками
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        plt.subplots_adjust(hspace=0.3, wspace=0.3)

        # График 1: Изменение длины очереди
        if self.results.get('queue_length_time_series'):
            times, lengths = zip(
                *sorted(self.results['queue_length_time_series']))
            axs[0, 0].plot(times, lengths, linewidth=1.5)
            axs[0, 0].set_title('Изменение длины очереди во времени')
            axs[0, 0].set_xlabel('Время (мин)')
            axs[0, 0].set_ylabel('Длина очереди (чел.)')
            # Средняя длина очереди
            avg_queue_length = self.results.get('avg_queue_length', 0)
            axs[0, 0].axhline(y=avg_queue_length, color='r', linestyle='--',
                              label=f'Средняя: {avg_queue_length:.2f}')
            axs[0, 0].legend()

        # График 2: Гистограмма времени ожидания
        waiting_times = self.results.get('waiting_time_distribution', [])
        if waiting_times:
            sns.histplot(waiting_times, kde=True, ax=axs[0, 1])
            axs[0, 1].set_title('Распределение времени ожидания')
            axs[0, 1].set_xlabel('Время ожидания (мин)')
            axs[0, 1].set_ylabel('Количество покупателей')
            # Среднее время ожидания
            avg_waiting_time = self.results.get('avg_waiting_time', 0)
            axs[0, 1].axvline(x=avg_waiting_time, color='r', linestyle='--',
                              label=f'Среднее: {avg_waiting_time:.2f}')
            axs[0, 1].legend()

        # График 3: Гистограмма времени в магазине
        times_in_shop = self.results.get('time_in_shop_distribution', [])
        if times_in_shop:
            sns.histplot(times_in_shop, kde=True, ax=axs[1, 0])
            axs[1, 0].set_title('Время нахождения в магазине')
            axs[1, 0].set_xlabel('Время (мин)')
            axs[1, 0].set_ylabel('Количество покупателей')
            # Среднее время
            avg_time = self.results.get('avg_time_in_shop', 0)
            axs[1, 0].axvline(x=avg_time, color='r', linestyle='--',
                              label=f'Среднее: {avg_time:.2f}')
            axs[1, 0].legend()

        # График 4: Загрузка касс
        utilization = self.results.get('cash_desk_utilization', {})
        if utilization:
            # Сортировка по номеру кассы и создание понятных меток
            desk_ids = sorted(utilization.keys())
            desk_labels = [f'{desk_id + 1}' for desk_id in desk_ids]
            utilization_values = [utilization[desk_id] for desk_id in desk_ids]

            bars = axs[1, 1].bar(desk_labels, utilization_values,
                                 color=sns.color_palette("viridis", len(utilization)))

            # Добавление процентов над столбцами
            for bar in bars:
                height = bar.get_height()
                axs[1, 1].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                               f'{height:.1%}', ha='center', va='bottom')

            axs[1, 1].set_title('Загрузка кассовых узлов')
            axs[1, 1].set_xlabel('Номер кассы')
            axs[1, 1].set_ylabel('Коэффициент загрузки')
            axs[1, 1].set_ylim(0, 1.1)

            # Форматирование оси Y в процентах
            axs[1, 1].yaxis.set_major_formatter(
                plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

            # Среднее значение
            avg_utilization = self.results.get('avg_cash_desk_utilization', 0)
            axs[1, 1].axhline(y=avg_utilization, color='r', linestyle='--',
                              label=f'Средняя: {avg_utilization:.1%}')
            axs[1, 1].legend()

        fig.suptitle('Результаты симуляции работы магазина', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Корректировка для заголовка

        return fig
