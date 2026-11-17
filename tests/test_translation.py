from dublagem import translation


def test_split_text_respeita_o_limite_e_mantem_o_texto():
    text = "Primeira frase curta. " + "palavra " * 120 + "fim. Última frase!"
    chunks = translation.split_text(text, limit=100)
    assert all(len(c) <= 100 for c in chunks)
    assert " ".join(chunks).split() == text.split()


def test_usa_mymemory_quando_google_falha(monkeypatch):
    class Broken:
        def __init__(self, **_kwargs):
            pass

        def translate(self, _text):
            raise RuntimeError("bloqueado")

    used = {}

    class Fallback:
        def __init__(self, source, target):
            used.update(source=source, target=target)

        def translate(self, text):
            return f"[{text}]"

    monkeypatch.setattr(translation, "GoogleTranslator", Broken)
    monkeypatch.setattr(translation, "MyMemoryTranslator", Fallback)

    assert translation.translate("Hello. World.", "en", "pt") == "[Hello. World.]"
    assert used == {"source": "en-US", "target": "pt-BR"}
