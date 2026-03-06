import re
from typing import List, Tuple

from bot.content import (
    GLOSSARY_TEXT,
    LIABILITY_TEXT,
    MYTHS,
    ROLE_GUIDES,
    SOURCES,
    TEMPLATE_TEXTS,
    THEORY_TOPICS,
)


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



def excerpt(text: str, query: str, radius: int = 220) -> str:
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



def score_match(query: str, text: str, title: str = "") -> int:
    q = normalize(query)
    haystack = normalize(text)
    score = 0
    if title and q in normalize(title):
        score += 6
    if q in haystack:
        score += 4
    for word in q.split():
        if word in haystack:
            score += 1
    return score



def search_topics(query: str) -> List[Tuple[int, str, str]]:
    results = []
    for slug, topic in THEORY_TOPICS.items():
        haystack = " ".join([topic["title"], topic["text"], " ".join(topic["tags"])])
        score = score_match(query, haystack, topic["title"])
        if score:
            results.append((score, topic["title"], excerpt(topic["text"], query)))
    results.sort(key=lambda item: item[0], reverse=True)
    return results[:6]



def search_roles(query: str) -> List[str]:
    results = []
    for guide in ROLE_GUIDES.values():
        score = score_match(query, guide["text"], guide["title"])
        if score:
            results.append(f"- <b>{guide['title']}</b>\n  {excerpt(guide['text'], query)}")
    return results[:4]



def search_myths(query: str) -> List[str]:
    results = []
    for myth in MYTHS.values():
        score = score_match(query, myth["text"], myth["title"])
        if score:
            results.append(f"- <b>{myth['title']}</b>\n  {excerpt(myth['text'], query)}")
    return results[:4]



def search_templates(query: str) -> List[str]:
    results = []
    for item in TEMPLATE_TEXTS.values():
        score = score_match(query, item["text"], item["title"])
        if score:
            results.append(f"- <b>{item['title']}</b>\n  {excerpt(item['text'], query)}")
    return results[:4]



def search_quick_blocks(query: str) -> List[str]:
    blocks = [
        ("Глоссарий", GLOSSARY_TEXT),
        ("Виды ответственности", LIABILITY_TEXT),
    ]
    results = []
    for title, text in blocks:
        score = score_match(query, text, title)
        if score:
            results.append(f"- <b>{title}</b>\n  {excerpt(text, query)}")
    return results



def search_sources(query: str) -> List[str]:
    q = normalize(query)
    matches = []
    for source in SOURCES:
        haystack = normalize(f"{source['name']} {source['summary']}")
        if q in haystack or any(word in haystack for word in q.split()):
            matches.append(f"- <b>{source['name']}</b>\n  {source['summary']}\n  {source['url']}")
    return matches[:6]



def search_materials(query: str) -> str:
    topics = search_topics(query)
    roles = search_roles(query)
    myths = search_myths(query)
    templates = search_templates(query)
    blocks = search_quick_blocks(query)
    source_matches = search_sources(query)

    if not any([topics, roles, myths, templates, blocks, source_matches]):
        return (
            "<b>Ничего точного не найдено</b>\n\n"
            "Попробуй уточнить запрос. Например: персональные данные, дисциплина труда, дисциплинарные взыскания, коммерческая тайна, удаленная работа, код, ПВТР, инцидент."
        )

    lines = [f"<b>Результаты поиска</b>\nЗапрос: <i>{query}</i>"]

    if topics:
        lines.append("\n<b>Теория</b>")
        for _, title, snippet in topics:
            lines.append(f"- <b>{title}</b>\n  {snippet}")

    if roles:
        lines.append("\n<b>Разделы по ролям</b>")
        lines.extend(roles)

    if myths:
        lines.append("\n<b>Мифы и ошибки</b>")
        lines.extend(myths)

    if templates:
        lines.append("\n<b>Шаблоны и памятки</b>")
        lines.extend(templates)

    if blocks:
        lines.append("\n<b>Быстрые блоки</b>")
        lines.extend(blocks)

    if source_matches:
        lines.append("\n<b>Подходящие источники</b>")
        lines.extend(source_matches)

    return "\n\n".join(lines)
