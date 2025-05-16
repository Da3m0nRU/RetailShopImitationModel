import simpy
import random
import numpy as np
from collections import defaultdict


class ShopSimulation:
    """Класс имитационной модели магазина"""

    def __init__(self, params):
        """
        Инициализация модели с параметрами

        Args:
            params (dict): Словарь с параметрами модели
        """
        # Настройка seed для воспроизводимости результатов
        self.seed = params.get('seed', 42)
        random.seed(self.seed)
        np.random.seed(self.seed)

        # Параметры модели
        self.simulation_time = params.get(
            'simulation_time', 480)  # мин (8 часов)
        # среднее время между прибытиями клиентов (мин)
        self.customer_arrival_mean = params.get('customer_arrival_mean', 5)

        # Параметры времени выбора товаров
        self.shopping_time_dist = params.get('shopping_time_dist', 'normal')
        # среднее время выбора товаров (мин)
        self.shopping_time_mean = params.get('shopping_time_mean', 15)
        self.shopping_time_std = params.get(
            'shopping_time_std', 5)  # стандартное отклонение (мин)
        self.shopping_time_min = params.get(
            'shopping_time_min', 5)  # минимальное время (мин)
        self.shopping_time_max = params.get(
            'shopping_time_max', 30)  # максимальное время (мин)

        # Параметры обслуживания на кассе
        self.service_time_dist = params.get('service_time_dist', 'exponential')
        # среднее время обслуживания (мин)
        self.service_time_mean = params.get('service_time_mean', 3)
        self.service_time_std = params.get(
            'service_time_std', 1)  # стандартное отклонение (мин)
        # количество касс - преобразуем в int для безопасности
        self.num_cash_desks = int(params.get('num_cash_desks', 3))

        # Создание среды моделирования
        self.env = simpy.Environment()

        # Создание касс (ресурсов)
        self.cash_desks = simpy.Resource(
            self.env, capacity=self.num_cash_desks)

        # Добавляем список для отслеживания доступных касс и их занятости
        self.cash_desk_active = [False] * self.num_cash_desks
        self.available_cash_desks = list(range(self.num_cash_desks))

        # Статистика
        self.stats = {
            'customer_arrivals': 0,  # количество прибывших клиентов
            'customers_served': 0,   # количество обслуженных клиентов
            'total_time_in_shop': [],  # время нахождения в магазине
            'waiting_times': [],     # время ожидания в очереди
            # длина очереди (словарь время:длина)
            'queue_lengths': defaultdict(int),
            # занятость каждой кассы (время начала:время окончания)
            'cash_desk_usage': defaultdict(list),
            'current_time': 0,       # текущее время симуляции
        }

        # Результаты симуляции
        self.results = {}

    def generate_shopping_time(self):
        """Генерирует время выбора товаров согласно заданному распределению"""
        if self.shopping_time_dist == 'normal':
            # Нормальное распределение с ограничением снизу
            time = max(self.shopping_time_min,
                       np.random.normal(self.shopping_time_mean, self.shopping_time_std))
            return min(time, self.shopping_time_max)  # с ограничением сверху
        elif self.shopping_time_dist == 'uniform':
            # Равномерное распределение
            return np.random.uniform(self.shopping_time_min, self.shopping_time_max)
        else:
            # По умолчанию используем экспоненциальное распределение
            return max(self.shopping_time_min, np.random.exponential(self.shopping_time_mean))

    def generate_service_time(self):
        """Генерирует время обслуживания на кассе согласно заданному распределению"""
        if self.service_time_dist == 'normal':
            # Нормальное распределение с ограничением снизу
            return max(0.5, np.random.normal(self.service_time_mean, self.service_time_std))
        else:
            # По умолчанию используем экспоненциальное распределение
            return max(0.5, np.random.exponential(self.service_time_mean))

    def customer_process(self, customer_id):
        """Процесс движения покупателя по магазину"""
        # Фиксируем время прибытия
        arrival_time = self.env.now

        # Запись времени для статистики очереди
        self.stats['queue_lengths'][int(self.env.now)] = len(
            self.cash_desks.queue) + len(self.cash_desks.users)

        # Процесс выбора товаров
        shopping_time = self.generate_shopping_time()
        yield self.env.timeout(shopping_time)

        # Покупатель встает в очередь к кассе
        queue_join_time = self.env.now
        self.stats['queue_lengths'][int(self.env.now)] = len(
            self.cash_desks.queue) + len(self.cash_desks.users)

        # Процесс ожидания в очереди и обслуживания на кассе
        with self.cash_desks.request() as request:
            yield request

            # Покупатель дождался своей очереди
            queue_exit_time = self.env.now
            waiting_time = queue_exit_time - queue_join_time
            self.stats['waiting_times'].append(waiting_time)

            # Обслуживание на кассе
            service_time = self.generate_service_time()

            # Выбираем доступную кассу из пула
            cash_desk_id = None
            for i in range(self.num_cash_desks):
                if not self.cash_desk_active[i]:
                    cash_desk_id = i
                    self.cash_desk_active[i] = True
                    break

            # Если все кассы заняты, берем первую (такого не должно происходить с правильной логикой)
            if cash_desk_id is None:
                cash_desk_id = 0

            # Запись интервала занятости кассы
            self.stats['cash_desk_usage'][cash_desk_id].append(
                (self.env.now, self.env.now + service_time))

            yield self.env.timeout(service_time)

            # Освобождаем кассу
            if cash_desk_id is not None:
                self.cash_desk_active[cash_desk_id] = False

        # Покупатель покидает магазин
        exit_time = self.env.now
        total_time = exit_time - arrival_time
        self.stats['total_time_in_shop'].append(total_time)
        self.stats['customers_served'] += 1

        # Обновление статистики очереди
        self.stats['queue_lengths'][int(self.env.now)] = len(
            self.cash_desks.queue) + len(self.cash_desks.users)

    def customer_generator(self):
        """Генератор потока покупателей"""
        customer_id = 0

        while True:
            # Генерация интервала прибытия (экспоненциальное распределение)
            interarrival_time = np.random.exponential(
                self.customer_arrival_mean)
            yield self.env.timeout(interarrival_time)

            # Создание нового покупателя
            customer_id += 1
            self.stats['customer_arrivals'] += 1
            self.env.process(self.customer_process(customer_id))

    def run_simulation(self):
        """Запуск симуляции магазина"""
        # Запуск генератора покупателей
        self.env.process(self.customer_generator())

        # Запуск процесса мониторинга длины очереди
        self.env.process(self.monitor_queue())

        # Запуск симуляции
        self.env.run(until=self.simulation_time)

        # Расчет итоговых статистик
        self.calculate_results()

        return self.results

    def monitor_queue(self):
        """Процесс мониторинга длины очереди через равные интервалы"""
        while True:
            # Запись текущей длины очереди
            self.stats['queue_lengths'][int(self.env.now)] = len(
                self.cash_desks.queue) + len(self.cash_desks.users)
            yield self.env.timeout(1)  # мониторинг каждую минуту
            self.stats['current_time'] = self.env.now

    def calculate_results(self):
        """Расчет результатов симуляции по собранной статистике"""
        # Общие показатели
        self.results['total_customers_arrived'] = self.stats['customer_arrivals']
        self.results['total_customers_served'] = self.stats['customers_served']

        # Время нахождения в магазине
        if self.stats['total_time_in_shop']:
            self.results['avg_time_in_shop'] = np.mean(
                self.stats['total_time_in_shop'])
            self.results['max_time_in_shop'] = np.max(
                self.stats['total_time_in_shop'])
            self.results['time_in_shop_distribution'] = self.stats['total_time_in_shop']
        else:
            self.results['avg_time_in_shop'] = 0
            self.results['max_time_in_shop'] = 0
            self.results['time_in_shop_distribution'] = []

        # Время ожидания в очереди
        if self.stats['waiting_times']:
            self.results['avg_waiting_time'] = np.mean(
                self.stats['waiting_times'])
            self.results['max_waiting_time'] = np.max(
                self.stats['waiting_times'])
            self.results['waiting_time_distribution'] = self.stats['waiting_times']
        else:
            self.results['avg_waiting_time'] = 0
            self.results['max_waiting_time'] = 0
            self.results['waiting_time_distribution'] = []

        # Длина очереди
        queue_lengths = list(self.stats['queue_lengths'].values())
        if queue_lengths:
            self.results['avg_queue_length'] = np.mean(queue_lengths)
            self.results['max_queue_length'] = np.max(queue_lengths)
            self.results['queue_length_time_series'] = list(zip(
                self.stats['queue_lengths'].keys(),
                self.stats['queue_lengths'].values()
            ))
        else:
            self.results['avg_queue_length'] = 0
            self.results['max_queue_length'] = 0
            self.results['queue_length_time_series'] = []

        # Коэффициент загрузки кассовых узлов
        total_working_time = 0
        cash_desk_utilization = {}

        # Обрабатываем только реальные кассы (их количество ограничено num_cash_desks)
        for cash_desk_id, intervals in self.stats['cash_desk_usage'].items():
            # Проверяем, что cash_desk_id является числом и находится в диапазоне касс
            if isinstance(cash_desk_id, (int, np.integer)) and 0 <= cash_desk_id < self.num_cash_desks:
                working_time = sum(end - start for start, end in intervals)
                utilization = working_time / self.simulation_time
                cash_desk_utilization[cash_desk_id] = utilization
                total_working_time += working_time

        # Убедимся, что есть запись для каждой кассы, даже если она не использовалась
        for i in range(self.num_cash_desks):
            if i not in cash_desk_utilization:
                cash_desk_utilization[i] = 0.0

        self.results['cash_desk_utilization'] = cash_desk_utilization

        if self.num_cash_desks > 0:
            self.results['avg_cash_desk_utilization'] = total_working_time / \
                (self.simulation_time * self.num_cash_desks)
        else:
            self.results['avg_cash_desk_utilization'] = 0
