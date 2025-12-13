"""
exam.py — нечёткий поиск дубликатов товаров.

Модуль реализует двухэтапный алгоритм поиска дубликатов:
1. Грубый поиск кандидатов через TF-IDF/токен-оверлап
2. Точная оценка через лексическое сравнение с нормализацией

Протокол данных: CSV-like формат, каждая строка: ID<TAB>Название
Выход: JSON файл с найденными дубликатами
"""

import json
import re
import numpy as np

from pathlib import Path
from functools import lru_cache
from typing import List, Tuple, Any, Optional


# ==================== КОНФИГУРАЦИЯ ====================
# Все настраиваемые параметры вынесены в начало модуля

SIMILARITY_THRESHOLD: float = 0.80   # итоговый порог 0..1
TOP_K_CANDIDATES: int = 12        # число кандидатов для детальной дооценки
TFIDF_CHAR_NGRAM: Tuple = (2, 5)    # char ngram диапазон для TF-IDF (устойчивее для коротких названий)

# Пути к файлам
CATALOG_FILE = "catalog.txt"
NEW_FILE = "new_items.txt"
OUTPUT_FILE = "duplicates.json"

# Флаги обработки
USE_PREPROCESSING = True      # включить текстовую нормализацию перед векторизацией

# Регулярные выражения для нормализации текста (скомпилированы для производительности)
RE_DIGIT_LETTER = re.compile(r'([0-9])([a-zа-я])')
RE_LETTER_DIGIT = re.compile(r'([a-zа-я])([0-9])')
RE_DIGIT_SLASH_DIGIT = re.compile(r'(\d)\s*/\s*(\d)')
RE_PUNCTUATION = re.compile(r'[^\w\s\+\/\-]')
RE_MULTISPACE = re.compile(r'\s+')

# Словари для нормализации текста
UNIT_MAP = {
    'гб': 'gb', 'гигабайт': 'gb', 'гбайт': 'gb',
    'мб': 'mb', 'мм': 'mm', 'дюйм': 'inch', 'дюйма': 'inch'
}
GENERIC_MAP = {
    'телефон': '', 'смартфон': '', 'планшет': '',
    'робот-пылесос': 'robot vacuum', 'пылесос': 'vacuum'
}
BRAND_FIXES = {
    # пример: возможные мелкие нормализации брендов
    'huawei': 'huawei', 'huaweI': 'huawei'
}

COLOR_MAP = {
    'черный': 'black', 'белый': 'white', 'синий': 'blue',
    'красный': 'red', 'зеленый': 'green', 'желтый': 'yellow',
    'розовый': 'pink', 'фиолетовый': 'purple', 'серый': 'gray',
    'золотой': 'gold', 'серебристый': 'silver',
    # Английские версии
    'black': 'black', 'white': 'white', 'blue': 'blue',
    'red': 'red', 'green': 'green', 'yellow': 'yellow',
    'pink': 'pink', 'purple': 'purple', 'gray': 'gray',
    'gold': 'gold', 'silver': 'silver'
}

# Флаги доступности внешних библиотек
TFIDF_AVAILABLE: bool = False
RAPIDFUZZ_AVAILABLE: bool = False

# ==================== ИМПОРТ ОПЦИОНАЛЬНЫХ БИБЛИОТЕК ====================

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    TFIDF_AVAILABLE = True
except Exception:
    TFIDF_AVAILABLE = False

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except Exception:
    RAPIDFUZZ_AVAILABLE = False
    from difflib import SequenceMatcher

# ----------------- Функция 1: надежный погрузчик -----------------
def load_tab_file(path):
    """
    Загружает файл в формате ID<TAB>Title с автоматическим определением кодировки.
    
    Алгоритм:
    1. Пробует кодировки: utf-8, cp1251, utf-16
    2. Заменяет буквальные '\t' на реальную табуляцию
    3. Использует fallback разделение по 2+ пробелам при отсутствии табуляции
    
    Args:
        file_path: Путь к файлу для загрузки
        
    Returns:
        Кортеж (список идентификаторов, список названий)
        
    Raises:
        FileNotFoundError: Если файл не существует
        IOError: Если не удалось прочитать файл ни в одной кодировке
    """
    encodings_to_try = ['utf-8', 'cp1251', 'utf-16']
    raw_lines = None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Попытка чтения в разных кодировках
    for enc in encodings_to_try:
        try:
            with open(path, encoding=enc) as f:
                raw_lines = [ln.rstrip("\n\r") for ln in f]
            print(f"[DEBUG] Loaded {path} with encoding {enc}, {len(raw_lines)} lines")
            break
        except Exception:
            raw_lines = None
    if raw_lines is None:
        raise IOError(f"Cannot read file {path} with encodings {encodings_to_try}")

    ids = []
    titles = []
    for ln in raw_lines:
        if not ln or not ln.strip():
            continue
        # Если в файле фигурирует буквальная последовательность '\t' — заменяем
        if '\\t' in ln:
            ln = ln.replace('\\t', '\t')
            
        # Разделение строки на ID и Title
        if "\t" in ln:
            parts = ln.split("\t", 1)  # Разделяем только по первому табу
        else:
            # fallback: split по 2+ пробелам
            parts = re.split(r"\s{1,}", ln, maxsplit=1)
            if len(parts) == 1:
                parts = ln.split(" ", 1)  # last resort
        if len(parts) != 2:
            print(f"[WARN] skipping malformed line in {path!r}: {ln!r}")
            continue
        ids.append(parts[0].strip())
        titles.append(parts[1].strip())
    return ids, titles

# ----------------- Функция 2: Нормализовать текст -----------------
# Правила нормализации: lower, унификация единиц, удаление лишних символов,
# разделение границ, сохранение + и / (для S10+ и 8/256)

def normalize_text(s: str):
    """
    Нормализует название товара для улучшения сравнения.
    
    Выполняет последовательность преобразований:
    1. Приведение к нижнему регистру
    2. Стандартизация единиц измерения (ГБ → GB)
    3. Удаление/замена общих слов
    4. Стандартизация цветов
    5. Разделение цифро-буквенных границ
    6. Удаление лишних символов
    
    Args:
        text: Исходное название товара
        
    Returns:
        Нормализованная строка
    """
    if USE_PREPROCESSING:
        if not s:
            return ""
        # Приведение к нижнему регистру
        s0 = s.lower()
        # заменить кавычки на дюймы
        s0 = s0.replace('"', ' inch ').replace('”', ' inch ').replace('“', ' inch ')
        # заменить блоки
        for k, v in UNIT_MAP.items():
            s0 = re.sub(r'\b' + re.escape(k) + r'\b', v, s0)
        # удаление или сопоставление общих слов
        for k, v in GENERIC_MAP.items():
            s0 = re.sub(r'\b' + re.escape(k) + r'\b', v, s0)
        # цвета
        for k, v in COLOR_MAP.items():
            s0 = re.sub(r'\b' + re.escape(k) + r'\b', v, s0)
        # отдельные границы между цифрами и буквами: "8/256GB" -> "8/256 gb" т.д.
        s0 = RE_DIGIT_SLASH_DIGIT.sub(r'\1/\2', s0)
        s0 = RE_DIGIT_LETTER.sub(r'\1 \2', s0)
        s0 = RE_LETTER_DIGIT.sub(r'\1 \2', s0)
        # сохранить плюс, косую черту, тире; убрать другие знаки препинания
        s0 = RE_PUNCTUATION.sub(' ', s0)
        s0 = RE_MULTISPACE.sub(' ', s0).strip()
        # дополнительные небольшие фирменные исправления
        for k, v in BRAND_FIXES.items():
            s0 = s0.replace(k, v)
        return s0

@lru_cache(maxsize=10000)
def normalize_text_cached(s: str):
    """
    Кэшированная версия функции normalize_text.
    
    Ускоряет обработку при повторяющихся названиях за счёт
    сохранения результатов в LRU кэше.
    
    Args:
        text: Исходное название товара
        
    Returns:
        Нормализованная строка (из кэша или новая)
    """
    return normalize_text(s)

# ----------------- Функция 3: Безопасное заполнение пустоты -----------------
def safe_fill_empty(norm_list, orig_list):
    """
    Заменяет пустые нормализованные строки на запасные токены.
    
    Это предотвращает ошибки при построении TF-IDF матрицы,
    когда некоторые названия после нормализации становятся пустыми.
    
    Алгоритм:
    - Если нормализованная строка не пуста, оставляем как есть
    - Если пуста, берём первые 1-2 слова из оригинала
    
    Args:
        normalized_list: Список нормализованных строк
        original_list: Список исходных строк
        
    Returns:
        Список нормализованных строк без пустых значений
    """
    out = []
    for norm, orig in zip(norm_list, orig_list):
        if norm and norm.strip():
            out.append(norm)
            continue
        s = (orig or "").lower()
        s = re.sub(r'[^\w\s\+\/\-]', ' ', s)
        toks = [tok for tok in s.split() if tok]
        fill = " ".join(toks[:2]) if toks else "emptytoken"
        out.append(fill)
    return out

# ----------------- Функция 4: Лексический показатель -----------------
@lru_cache(maxsize=50000)
def lexical_score(a: str, b: str) -> float:
    """
    Вычисляет лексическое сходство между двумя строками в диапазоне [0, 1].
    
    Использует двухэтапный алгоритм:
    1. Если доступен rapidfuzz: token_set_ratio (наиболее точный)
    2. Иначе: комбинация Jaccard схожести токенов и SequenceMatcher
    
    Args:
        text_a: Первая строка для сравнения
        text_b: Вторая строка для сравнения
        
    Returns:
        Оценка схожести от 0.0 (разные) до 1.0 (идентичные)
    """
    if RAPIDFUZZ_AVAILABLE:
        try:
            return fuzz.token_set_ratio(a, b) / 100.0
        except Exception:
            pass
    # fallback
    a_tokens = frozenset(a.split())
    b_tokens = frozenset(b.split())
    if not a_tokens and not b_tokens:
        return 1.0
    inter = a_tokens & b_tokens
    jacc = len(inter) / max(1, len(a_tokens | b_tokens))
    seq = SequenceMatcher(None, a, b).ratio()
    return 0.6 * jacc + 0.4 * seq

# ----------------- Функция 5: Построить tfidf_index -----------------
def build_tfidf_index(cat_norm, new_norm):
    """
    Строит TF-IDF индексы для грубого поиска кандидатов.
    
    Алгоритм:
    1. Объединяет все тексты для построения словаря
    2. Пытается использовать char n-grams (устойчивее для коротких названий)
    3. При ошибке переключается на word n-grams
    
    Args:
        catalog_texts: Нормализованные тексты каталога
        new_texts: Нормализованные тексты новых товаров
        
    Returns:
        Кортеж (vectorizer, cat_tfidf_matrix, new_tfidf_matrix)
        Если sklearn недоступен, возвращает (None, None, None)
    """
    if not TFIDF_AVAILABLE:
        return None, None, None
    all_docs = cat_norm + new_norm
    try:
        vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=TFIDF_CHAR_NGRAM, min_df=1)
        vectorizer.fit(all_docs)
    except Exception:
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,2), token_pattern=r"(?u)\b\w+\b", min_df=1)
        vectorizer.fit(all_docs)
    cat_tfidf = vectorizer.transform(cat_norm)
    new_tfidf = vectorizer.transform(new_norm)
    return vectorizer, cat_tfidf, new_tfidf

# ----------------- Функция 6: Поиск кандидата -----------------
def candidate_search(i_new, new_norm_text, cat_tfidf, new_tfidf, cat_tokens, cat_norm_all, top_k=TOP_K_CANDIDATES):
    """
    Выполняет грубый поиск кандидатов-дубликатов для нового товара.
    
    Двухэтапная стратегия:
    1. Если доступен TF-IDF: косинусное сходство
    2. Иначе: Jaccard overlap токенов (fallback)
    
    Args:
        new_item_index: Индекс нового товара в списке
        new_item_text: Нормализованный текст нового товара
        catalog_tfidf: TF-IDF матрица каталога
        new_tfidf: TF-IDF матрица новых товаров
        catalog_normalized: Список нормализованных текстов каталога
        catalog_tokens: Предвычисленные токены каталога (для fallback)
        top_k: Максимальное количество возвращаемых кандидатов
        
    Returns:
        Список кортежей (индекс_в_каталоге, оценка_сходства)
    """
    if TFIDF_AVAILABLE and cat_tfidf is not None and new_tfidf is not None:
        try:
            v = new_tfidf[i_new]
            sims = linear_kernel(v, cat_tfidf).flatten()
            idxs = sims.argsort()[::-1][:top_k]
            return [(int(j), float(sims[j])) for j in idxs]
        except Exception as e:
            raise e
    else:
        # token overlap
        ntoks = set(new_norm_text.split())
        scores = []
        for j, ctoks in enumerate(cat_tokens):
            jacc = len(ntoks & ctoks) / max(1, len(ntoks | ctoks))
            scores.append((j, jacc))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
def batch_candidate_search_tfidf(new_tfidf: Any, 
                                cat_tfidf: Any, 
                                top_k: int=TOP_K_CANDIDATES
                                ) -> Optional[List[List[Tuple[int, float]]]]:
    """
    Выполняет пакетный поиск кандидатов-дубликатов для всех новых товаров одновременно.
    
    Алгоритм:
    1. Вычисляет матрицу косинусных сходств между всеми новыми товарами и каталогом
    2. Для каждого нового товара выбирает top_k наиболее похожих товаров из каталога
    3. Возвращает результаты в структурированном виде
    
    Преимущества перед последовательным поиском:
    - Векторизованные вычисления (быстрее для больших объемов)
    - Минимизация накладных расходов на вызовы функций
    - Эффективное использование кэша процессора
    
    Args:
        new_tfidf: TF-IDF матрица новых товаров, shape (M, V)
        cat_tfidf: TF-IDF матрица каталога, shape (N, V)
        top_k: Максимальное количество кандидатов для каждого товара
        
    Returns:
        Список списков, где:
        - Внешний список соответствует новым товарам
        - Внутренний список содержит кортежи (индекс_в_каталоге, оценка_сходства)
        - Возвращает None в случае ошибки или недоступности TF-IDF
        
    Raises:
        Не генерирует исключения напрямую, возвращает None при ошибках
    """
    if not TFIDF_AVAILABLE or cat_tfidf is None or new_tfidf is None:
        return None
    
    try:
        # Вычисляем все попарные сходства за один вызов
        sim_matrix = linear_kernel(new_tfidf, cat_tfidf)  # Форма (M, N)
        
        # Получаем количество новых товаров
        n_new = sim_matrix.shape[0]
        n_cat = sim_matrix.shape[1]
        
        # Если кандидатов меньше, чем top_k, используем всех
        actual_top_k = min(top_k, n_cat)
        
        # Находим top_k для каждой строки
        top_indices = np.argsort(-sim_matrix, axis=1)[:, :actual_top_k]
        
        # Собираем результаты
        results = []
        for i in range(n_new):
            row_indices = top_indices[i]
            row_scores = sim_matrix[i, row_indices]
            results.append([(int(idx), float(score)) 
                        for idx, score in zip(row_indices, row_scores)])
        
        return results
    except Exception as e:
        print(f"[WARN] Batch candidate search failed: {e}")
        return None

# ----------------- Функция 7: Вычислительный комбинированный результат -----------------
def compute_combined_score(a_norm, b_norm, coarse_sim):
    """
    Вычисляет итоговую оценку схожести через комбинацию метрик.
    
    Комбинирует:
    - Лексическое сходство (precision-ориентированное)
    - TF-IDF сходство (recall-ориентированное)
    
    Args:
        text_a_normalized: Первая нормализованная строка
        text_b_normalized: Вторая нормализованная строка
        coarse_similarity: Грубая оценка сходства (TF-IDF или Jaccard)
        
    Returns:
        Кортеж (lexical_score, tfidf_score, combined_score)
    """
    lex = lexical_score(a_norm, b_norm)
    tfidf_sim_norm = float(coarse_sim) if coarse_sim is not None else 0.0
    combined = 0.6 * lex + 0.4 * tfidf_sim_norm
    return round(lex, 4), round(tfidf_sim_norm, 4), round(combined, 4)

# ----------------- Функция 8: Полный цикл процессов -----------------
def process_all(cat_ids, cat_titles, new_ids, new_titles):
    """
    Основной процесс поиска дубликатов.
    
    Алгоритм:
    1. Нормализация и предобработка текстов
    2. Построение индексов для быстрого поиска
    3. Для каждого нового товара:
       - Грубый поиск кандидатов
       - Точная оценка кандидатов
       - Фильтрация по порогу
    4. Формирование результатов
    
    Args:
        catalog_ids: Идентификаторы товаров в каталоге
        catalog_titles: Названия товаров в каталоге
        new_ids: Идентификаторы новых товаров
        new_titles: Названия новых товаров
        
    Returns:
        Словарь с результатами поиска, готовый для сохранения в JSON
    """
    # Нормализации
    cat_norm_local = [normalize_text_cached(t) for t in cat_titles]
    new_norm_local = [normalize_text_cached(t) for t in new_titles]

    # Защита от пустых нормализованных строк
    cat_norm_local = safe_fill_empty(cat_norm_local, cat_titles)
    new_norm_local = safe_fill_empty(new_norm_local, new_titles)

    # Построение TF-IDF (если возможно)
    vectorizer, cat_tfidf, new_tfidf = build_tfidf_index(cat_norm_local, new_norm_local)

    # подготовка токенов для fallback поиска
    cat_tokens_local = [set(s.split()) for s in cat_norm_local] if not TFIDF_AVAILABLE else None
    # ПАКЕТНЫЙ поиск кандидатов (если TF-IDF доступен)
    if TFIDF_AVAILABLE and cat_tfidf is not None:
        batch_candidates = batch_candidate_search_tfidf(new_tfidf, cat_tfidf, TOP_K_CANDIDATES)
    else:
        batch_candidates = None

    results = {}

    for i, nid in enumerate(new_ids):
        detailed = []
        if batch_candidates is not None:
            cand_list = batch_candidates[i]
        else:
            cand_list = candidate_search(
                i, 
                new_norm_local[i],
                cat_tfidf, 
                new_tfidf, 
                cat_tokens_local, 
                cat_norm_local,
                top_k=TOP_K_CANDIDATES
            )
        for idx, coarse_sim in cand_list:
            a_norm = new_norm_local[i]
            b_norm = cat_norm_local[idx]
            lex, tfidf_norm, combined = compute_combined_score(a_norm, b_norm, coarse_sim)
            detailed.append({
                "catalog_id": cat_ids[idx],
                "catalog_title": cat_titles[idx],
                "catalog_norm": b_norm,
                "score_components": {"lexical": lex, "tfidf": tfidf_norm},
                "score": combined
            })
        # фильтрация по порогу
        filtered = [d for d in detailed if d["score"] >= SIMILARITY_THRESHOLD]
        filtered.sort(key=lambda x: x["score"], reverse=True)
        results[nid] = {
            "new_title": new_titles[i],
            "new_norm": new_norm_local[i],
            "matches": filtered
        }
    return results

# ----------------- Функция 9: Сохраняем результат -----------------
def save_results(results, out_path=OUTPUT_FILE):
    """
    Сохраняет результаты поиска в JSON файл.
    
    Args:
        results: Словарь с результатами поиска
        output_path: Путь для сохранения JSON файла
    """
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Saved results to {out_path}")

# ----------------- main -----------------
def main():
    """
    Главная функция приложения.
    
    Выполняет полный цикл:
    1. Загрузка данных
    2. Поиск дубликатов
    3. Сохранение результатов
    """
    print("[INFO] Starting duplicate-finder pipeline")
    cat_ids, cat_titles = load_tab_file(CATALOG_FILE)
    new_ids, new_titles = load_tab_file(NEW_FILE)
    if not cat_ids:
        print("[WARN] catalog appears empty after parsing — check file format and encoding")
    if not new_ids:
        print("[WARN] new_items appears empty after parsing — nothing to do")
    results = process_all(cat_ids, cat_titles, new_ids, new_titles)
    save_results(results)

    # краткий вывод в консоль
    for nid, info in results.items():
        print(f"\nNew {nid}: {info['new_title']}")
        if not info['matches']:
            print("  -> No matches above threshold")
        else:
            for m in info['matches']:
                print(f"  -> {m['catalog_id']}: {m['catalog_title']} (score={m['score']})")

if __name__ == "__main__":
    main()
