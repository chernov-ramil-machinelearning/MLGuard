# 🛡️ MLGuard

> Линтер для предиктивной аналитики бизнеса - находит методологические и статистические ловушки в данных без вреда продакшену.

[![CI](https://github.com/chernov-ramil-machinelearning/MLGuard/actions/workflows/ci.yml/badge.svg)](https://github.com/chernov-ramil-machinelearning/MLGuard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

---

## Что делает проект

MLGuard - это CLI-инструмент и библиотека, которая проверяет табличные данные (`.csv`, `.parquet`) на набор типовых математических и методологических ошибок, из-за которых предиктивная аналитика и ML-модели дают ложную уверенность в результатах.

В библиотеке реализовано 5 автономных проверок:

| Проверка | Что ищет | Математический аппарат |
|---|---|---|
| `leakage_detector` | Утечка таргета через скоррелированные признаки и мультиколлинеарность | Модуль корреляции Пирсона, пороговый анализ |
| `small_sample_guard` | Недостаточный объём данных, дисбаланс классов и нестабильность метрик | Bootstrap-доверительные интервалы (1000 ресэмплов) |
| `churn_blindness` | Survivorship Bias - анализ только на "выживших" клиентах | Двухвыборочный тест Колмогорова-Смирнова (`ks_2samp`) |
| `metric_confusion` | Расхождение метрики привлечения и метрики здоровья бизнеса | Непараметрический тест Манна-Кендалла на тренд (`kendalltau`) |
| `seasonality_sentiment` | Сезонность, маскирующая реальный тренд в данных | STL-декомпозиция ряда на Trend, Seasonal, Residual |

---

## Почему это полезно

MLGuard не заменяет инструменты валидации типов данных вроде `great_expectations` или `pandera` - он решает более глубокую задачу: автоматически находит статистические и методологические ловушки (Data Leakage, Survivorship Bias, Vanity Metrics, нерепрезентативный размер выборки, скрытая сезонность), которые обычно требуют экспертизы в матстате. 

Идея в том, чтобы упаковать эту статистическую экспертизу в готовые автономные проверки.

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
[CRITICAL] leakage_detector     leaky_corr_feature   Feature 'leaky_corr_feature' has a correlation of 0.9961 with target 'target'.
[WARNING]  small_sample_guard   all                  Sample size (100) is below the minimum threshold (200).
[CRITICAL] churn_blindness      salary               Distribution shift detected for 'salary' between active and churned clients (p-value = 0.0000).

Итого: 3 findings - 2 critical, 1 warning.
```

### Основные команды

```bash
mlguard checks list                                  # список доступных проверок
mlguard audit data.csv --format json -o report.json  # отчёт в формате JSON
mlguard audit data.csv --format markdown              # отчёт в формате Markdown
mlguard audit data.csv --only leakage_detector,churn_blindness
mlguard audit data.csv --fail-on WARNING              # gate для CI/CD: exit code 1 при находках >= WARNING
```

### Конфигурация (`mlguard.toml`)

Чтобы не передавать флаги каждый раз, создайте `mlguard.toml` в корне проекта:

```toml
[mlguard]
target_col = "churn"
time_col = "created_at"
fail_on = "CRITICAL"
format = "table"
```

Приоритет: CLI-флаги переопределяют `mlguard.toml`, который переопределяет дефолтные значения.

---

## Использование в CI/CD (GitHub Actions)

Пример пайплайна в `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]
      - name: Run audit test
        run: |
          python -m mlguard.core.runner
```

Если проверка сбоит или находит критические ошибки - пайплайн блокирует мёрдж PR.

---

## Автор и поддержка

Учебный и коммерческий проект, разработанный в процессе подготовки к отбору в Т-Академию (Т-Банк). Цель - довести идею от математической концепции до работающего инструмента: 5 статистических проверок, CLI, конфигурация, готовность к CI/CD.

* **Автор**: [Рамиль Чернов](https://github.com/chernov-ramil-machinelearning)
* **Telegram**: [@NoApexDB](https://t.me/NoApexDB)

## Лицензия

MIT - см. файл [LICENSE](LICENSE).
