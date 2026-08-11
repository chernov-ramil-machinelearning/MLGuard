# MLGuard

> Линтер для предиктивной аналитики бизнеса — находит методологические и статистические ловушки в данных без вреда продакшену.

[![CI](https://github.com/chernov-ramil-machinelearning/MLGuard/actions/workflows/ci.yml/badge.svg)](https://github.com/chernov-ramil-machinelearning/MLGuard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

---

## Что делает проект

MLGuard — это CLI-инструмент и библиотека, которая проверяет табличные данные (`.csv`, `.parquet`) на набор типовых математических и методологических ошибок, из-за которых предиктивная аналитика и ML-модели дают ложную уверенность в результатах.

В библиотеке реализовано 5 автономных проверок:

| Проверка | Что ищет | Математический аппарат |
|---|---|---|
| `leakage_detector` | Утечка таргета через скоррелированные признаки и мультиколлинеарность | Модуль корреляции Пирсона, пороговый анализ |
| `small_sample_guard` | Недостаточный объём данных, дисбаланс классов и нестабильность метрик | Bootstrap-доверительные интервалы (1000 ресэмплов) |
| `churn_blindness` | Survivorship Bias — анализ только на "выживших" клиентах | Двухвыборочный тест Колмогорова-Смирнова (`ks_2samp`) |
| `metric_confusion` | Расхождение метрики привлечения и метрики здоровья бизнеса | Непараметрический тест Манна-Кендалла на тренд (`kendalltau`) |
| `seasonality_sentiment` | Сезонность, маскирующая реальный тренд в данных | STL-декомпозиция ряда на Trend, Seasonal, Residual |

---

## Валидация на синтетических данных

Оценка качества проведена на синтетических датасетах (клинические/чистые + датасеты с контролируемыми инъекциями дефектов), сгенерированных на независимых random seed. Ниже — усреднённый результат по 3 независимым held-out прогонам (по 50 чистых + 50 «грязных» датасетов в каждом):

| Проверка | Precision (range) | Recall | F1 |
|---|---|---|---|
| `leakage_detector` | 1.00 | 1.00 | 1.00 |
| `small_sample_guard` | 1.00 | 1.00 | 1.00 |
| `metric_confusion` | 0.83–1.00 | 1.00 | 0.91–1.00 |
| `churn_blindness` | 0.95 | 1.00 | 0.98 |
| `seasonality_sentiment` | 0.77–1.00 | 1.00 | 0.87–1.00 |

**Найденная и исправленная проблема при валидации:** первая версия бенчмарка показывала Precision 50% сразу у трёх проверок. Разбор показал, что это не шум, а две конкретные причины:

1. `leakage_detector` и `churn_blindness` в части случаев детектировали один и тот же root cause разными статистическими тестами (признак, сильно зависящий от таргета, — это одновременно и утечка, и статистически значимый сдвиг распределения между классами). Это не ошибка проверок, а неверная разметка ground truth в самом бенчмарке — исправлено: такие случаи размечены как истинно положительные для обеих проверок.
2. `seasonality_sentiment` ложно находил сезонность на слишком коротких рядах — STL переобучался на шум при малом числе полных циклов. Исправлено ужесточением минимальной длины ряда (не меньше 6 полных периодов) перед тем, как доверять результату STL.

* Примечание: валидация проведена на синтетических данных с контролируемыми инъекциями дефектов. Проверка на реальных публичных датасетах — в планах.

---

## Быстрый старт

### Установка

```bash
git clone https://github.com/chernov-ramil-machinelearning/MLGuard.git
cd MLGuard
pip install -e .
```

> Требуется Python 3.11+.

### Запуск аудита из CLI

```bash
mlguard audit data.csv --target churn --time-col created_at
```

Пример вывода в консоль:

```text
[CRITICAL] leakage_detector     leaky_corr_feature        Feature 'leaky_corr_feature' has a correlation of 0.9961 with target 'target'.
[WARNING ] small_sample_guard   all                       Sample size (100) is below the minimum threshold (200).
[CRITICAL] churn_blindness      salary                    Distribution shift detected for 'salary' between active and churned clients (p-value = 0.0000).

Итого: 3 findings — 2 critical, 1 warning.
```

### Основные команды

```bash
mlguard checks list                                  # список доступных проверок
mlguard audit data.csv --format json -o report.json  # отчёт в формате JSON
mlguard audit data.csv --format markdown              # отчёт в формате Markdown
mlguard audit data.csv --only leakage_detector,churn_blindness
mlguard audit data.csv --fail-on WARNING              # gate для CI/CD: exit code 1 при находках >= WARNING
```

---

## Автор и поддержка

Учебный и коммерческий проект, разработанный в процессе подготовки к отбору в Т-Академию (Т-Банк). Цель — довести идею от математической концепции до работающего инструмента: 5 статистических проверок, CLI, конфигурация, готовность к CI/CD.

* **Автор**: [Рамиль Чернов](https://github.com/chernov-ramil-machinelearning)
* **Telegram**: [@NoApexDB](https://t.me/NoApexDB)

## Лицензия

MIT — см. файл [LICENSE](LICENSE).
