class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class SectionNotFoundException(Exception):
    """Исключение для случаев отсутствия ожидаемых элементов на странице."""
