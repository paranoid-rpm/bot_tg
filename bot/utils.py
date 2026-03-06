import re
from typing import List, Tuple

from bot.content import SOURCES, TOPICS


def normalize(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_text(text: str, limit: int = 3800) -> List[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = []
    current_len = 0

    for paragraph in text.split("\n\n"):
        paragraph_len = len(paragraph) + 2
        if current and current_len + paragraph_len > limit:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += paragraph_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def excerpt(text: str, query: str, radius: int = 180) -> str:
    normalized_text = normalize(text)
    normalized_query = normalize(query)
    index = normalized_text.find(normalized_query)
    if index == -1:
        return text[:radius].strip() + ("..." if len(text) > radius else "")

    start = max(0, index - radius // 2)
    end = min(len(text), index + len(query) + radius)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet += "..."
    return snippet


def search_topics(query: str) -> List[Tuple[int, str, str]]:
    q = normalize(query)
    results = []

    for slug, topic in TOPICS.items():
        haystack = " ".join([topic["title"], topic["text"], " ".join(topic["tags"])])
        normalized_haystack = normalize(haystack)

        score = 0
        if q in normalize(topic["title"]):
            score += 5
        if q in normalized_haystack:
            score += 3
        for word in q.split():
            if word in normalized_haystack:
                score += 1
        if score:
            results.append((score, slug, excerpt(topic["text"], query)))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:5]



def search_sources(query: str) -> List[str]:
    q = normalize(query)
    matches = []
    for source in SOURCES:
        haystack = normalize(f"{source['name']} {source['summary']}")
        if q in haystack or any(word in haystack for word in q.split()):
            matches.append(f"- <b>{source['name']}</b>\n  {source['summary']}\n  {source['url']}")
    return matches[:5]



def search_materials(query: str) -> str:
    topics = search_topics(query)
    source_matches = search_sources(query)

    if not topics and not source_matches:
        return (
            "<b>Ничего точного не найдено</b>\n\n"
            "Попробуй уточнить запрос. Например: персональные данные, дисциплина труда, коммерческая тайна, код, ПВТР, утечка."
        )

    lines = [f"<b>Результаты поиска</b>\nЗапрос: <i>{query}</i>"]

    if topics:
        lines.append("\n<b>Подходящие разделы</b>")
        for score, slug, snippet in topics:
            lines.append(f"- <b>{TOPICS[slug]['title']}</b>\n  {snippet}\n  Открой раздел через кнопку «📚 Разделы».")

    if source_matches:
        lines.append("\n<b>Подходящие источники</b>")
        lines.extend(source_matches)

    return "\n\n".join(lines)
