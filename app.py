import os

import streamlit as st
from urllib.parse import quote

TUTOR_AVATAR = "data:image/svg+xml;utf8," + quote('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><defs><radialGradient id="b" cx=".3" cy=".2" r=".9"><stop stop-color="#b9a0f0"/><stop offset=".4" stop-color="#9675dd"/><stop offset="1" stop-color="#603a9e"/></radialGradient></defs><path d="M7 42C5 29 13 12 29 10C47 8 58 22 57 39C58 49 49 53 33 53C16 53 8 51 7 42Z" fill="url(#b)" stroke="#6842a6" stroke-width="2"/><ellipse cx="23" cy="31" rx="4" ry="6" fill="#fff9ff"/><ellipse cx="42" cy="31" rx="4" ry="6" fill="#fff9ff"/><path d="M29 42Q33 46 37 42" fill="none" stroke="#4e297f" stroke-width="2" stroke-linecap="round"/></svg>')

from analyzer import analyze_text
from tutor_agent import ask_tutor


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HanLevel v1.0",
    page_icon=TUTOR_AVATAR,
    layout="centered",
)


# =========================================================

import re

# Compact language control above the header, aligned to the right.
with st.container(key="language_switch"):
    language = st.selectbox(
        "Language / Idioma",
        ["English", "Português", "Español"],
        key="interface_language",
        label_visibility="collapsed",
    )

TRANSLATIONS = {
'Korean Readability Profiler':'Analisador de legibilidade do coreano',
'Korean Readability Profiler · AI Tutor':'Analisador de legibilidade do coreano · Tutor de IA',
'Know if a Korean text is right for your level':'Descubra se um texto em coreano é adequado ao seu nível',
' — and understand why. ':' — e entenda o motivo. ',
'HanLevel analyzes vocabulary, grammar, and sentence length to estimate how challenging a Korean text may be.':'O HanLevel analisa vocabulário, gramática e extensão das frases para estimar a dificuldade de um texto em coreano.',
'Korean text':'Texto em coreano','Analyze difficulty':'Analisar dificuldade','Tell Lívia':'Fale com Lívia',
'Please enter some Korean text first.':'Insira um texto em coreano primeiro.','Analyzing Korean text...':'Analisando o texto em coreano...',
'Estimated difficulty':'Dificuldade estimada','Estimated level':'Nível estimado','HanLevel score:':'Pontuação HanLevel:',
'Readability profile':'Perfil de legibilidade','Vocabulary difficulty':'Dificuldade do vocabulário','Grammar complexity':'Complexidade gramatical','Sentence length':'Extensão das frases','Vocabulary':'Vocabulário','Grammar':'Gramática',
'Beginner':'Iniciante','Intermediate':'Intermediário','Advanced':'Avançado','Unclassified':'Não classificado',
'Higher scores indicate greater estimated difficulty.':'Pontuações mais altas indicam maior dificuldade estimada.',
'Contribution to HanLevel score':'Contribuição para a pontuação HanLevel',' points':' pontos',
'Weighted contributions add up to the final HanLevel score.':'As contribuições ponderadas somam a pontuação final do HanLevel.',
'See analysis details':'Ver detalhes da análise','Dictionary coverage:':'Cobertura do dicionário:',
'Average eojeol per sentence:':'Média de eojeol por frase:','Vocabulary profile':'Perfil do vocabulário',
'Potentially challenging vocabulary':'Vocabulário potencialmente desafiador','Detected structural markers':'Marcadores estruturais identificados',
'Counts include repeated lexical items. The challenging-vocabulary list below shows each word only once.':'A contagem inclui itens lexicais repetidos. A lista abaixo apresenta cada palavra apenas uma vez.',
'No intermediate or advanced vocabulary was identified in the graded dictionary entries.':'Não foi identificado vocabulário intermediário ou avançado nas entradas classificadas do dicionário.',
'HanLevel detected ':'O HanLevel identificou ',' structural markers in total.':' marcadores estruturais no total.',
'No weighted structural markers were detected.':'Não foram identificados marcadores estruturais ponderados.',
'These markers are used by HanLevel\'s rule-based grammar-complexity component. They are structural indicators, not official learner-level grammar classifications.':'Esses marcadores são usados pelo componente de complexidade gramatical baseado em regras do HanLevel. São indicadores estruturais, não classificações oficiais de nível gramatical.',
'How HanLevel calculates difficulty':'Como o HanLevel calcula a dificuldade',
'Ask Mongle (몽글)':'Converse com Mongle (몽글)','Suggested questions':'Perguntas sugeridas',
'What does this text mean?':'O que este texto significa?','Explain the grammar':'Explique a gramática',
'Which words are difficult?':'Quais palavras são difíceis?','Make it easier':'Simplifique o texto','Make it more advanced':'Torne o texto mais avançado',
'Why is this ':'Por que este texto é ','Why ':'Por que ',
'Conversation':'Conversa','Ask me anything about this text':'Pergunte sobre este texto',
'e.g. Why is -는데 used here? Is there an easier word for this?':'Ex.: Por que -는데 aparece aqui? Existe uma palavra mais simples?',
'Send':'Enviar','thinking...':'pensando...',
'Hi ^^ I’m Mongle (몽글), your HanLevel Tutor. Pick a question above or type your own below. I\'ll stay focused on this text with you ^^':'Oi ^^ Sou Mongle (몽글), seu Tutor HanLevel. Escolha uma pergunta acima ou escreva a sua abaixo. Vamos explorar este texto juntos ^^',
'I couldn\'t finish that answer just now. Try me again in a moment? ^^':'Não consegui concluir a resposta agora. Tente novamente em instantes ^^',
'Found something wrong with the tutor?':'Encontrou algum problema com o tutor?','let us know':'Avise a gente',
'Hi ^^ I\'m the HanLevel Tutor.':'Oi ^^ Sou Mongle (몽글), seu Tutor HanLevel.',
'This is my creator,':'Minha criadora é',
'If I gave you an inaccurate explanation, hallucinated something,\n        or just acted a little weird, please tell her. It helps us make\n        this tutor better :)':'Se eu dei uma explicação incorreta, inventei alguma informação\n        ou me comportei de um jeito estranho, avise a ela. Isso nos ajuda\n        a melhorar o tutor :)',
'Email Lívia:':'Envie um e-mail para Lívia:',
'The private contact email has not been configured yet.':'O e-mail de contato ainda não foi configurado.',
'Technical details':'Detalhes técnicos',
'Ask about meaning, vocabulary, grammar, or how this\n                        Korean could be expressed differently. I\'m here to\n                        explore the text with you ^^':'Pergunte sobre o significado, o vocabulário, a gramática ou outras\n                        formas de expressar este texto em coreano. Vamos\n                        explorar o texto juntos ^^',
'The readability analysis works without AI, but the tutor needs GEMINI_API_KEY configured in this deployment.':'A análise de legibilidade funciona sem IA, mas o tutor está indisponível nesta configuração.',
'The text has ':'O texto apresenta ',' vocabulary difficulty, ':' dificuldade de vocabulário, ',
' grammatical complexity, and ':' complexidade gramatical e ',' sentence-length difficulty. ':' dificuldade relacionada à extensão das frases. ',
' contributes the most to the final score (+':' é o fator que mais contribui para a pontuação final (+',
'Most classified lexical items are ':'A maioria dos itens lexicais classificados pertence ao nível ',
' level. ':' . ','Sentences average ':'As frases têm, em média, ',' eojeol.':' eojeol.',
'low':'baixa','moderate':'moderada','high':'alta','beginner':'iniciante','intermediate':'intermediário','advanced':'avançado',
'Vocabulary coverage is limited, so the lexical estimate should be interpreted cautiously.':'A cobertura do vocabulário é limitada; interprete a estimativa lexical com cautela.',
'Limited vocabulary coverage (':'Cobertura limitada do vocabulário (',
'The difficulty estimate may be less reliable because many lexical items could not be assigned a learner level.':'A estimativa pode ser menos confiável porque muitos itens lexicais não puderam ser classificados por nível.',
'Prefinal ending':'Terminação pré-final','Connective ending':'Terminação conectiva','Adnominal ending':'Terminação adnominal','Nominalizing ending':'Terminação nominalizadora','Auxiliary verb':'Verbo auxiliar','Quotation particle':'Partícula de citação','Structural marker':'Marcador estrutural',
}

TRANSLATIONS["\nHanLevel combines three interpretable indicators:\n\n**Vocabulary difficulty — 45%**\n\nVocabulary is matched against learner-level information from the Korean Learners' Dictionary (한국어기초사전).\n\nBeginner entries receive a lower difficulty value, while intermediate and advanced entries contribute progressively more to the vocabulary score. Unclassified items do not automatically count as difficult.\n\n**Grammar & morphology — 35%**\n\nKorean morphological analysis is performed with Kiwi. Selected structural markers and morphological density contribute to the grammar-complexity score.\n\nThe grammar score represents structural complexity. It should not be interpreted as an official grammar proficiency level.\n\n**Sentence length — 20%**\n\nAverage eojeol per sentence is used as an additional structural-complexity indicator.\n\n**Final classification**\n\nThe three components are combined into the HanLevel score.\n\nCurrent provisional thresholds are:\n\n- **Beginner:** below 25\n- **Intermediate:** 25 to below 50\n- **Advanced:** 50 and above\n\nThese thresholds were calibrated on a small internally constructed development set. They are not official TOPIK or CEFR boundaries.\n\nHanLevel v0.1 uses a rule-based model designed to make its difficulty estimate transparent and inspectable.\n"] = '\nO HanLevel combina três indicadores interpretáveis:\n\n**Dificuldade do vocabulário — 45%**\n\nO vocabulário é comparado com as informações de nível do Dicionário de Coreano para Aprendizes (한국어기초사전). Entradas iniciantes recebem valores menores, enquanto entradas intermediárias e avançadas contribuem progressivamente mais. Itens sem classificação não são automaticamente considerados difíceis.\n\n**Gramática e morfologia — 35%**\n\nA análise morfológica do coreano é realizada com o Kiwi. Marcadores estruturais selecionados e a densidade morfológica contribuem para a complexidade gramatical. Essa pontuação indica complexidade estrutural, não um nível oficial de proficiência gramatical.\n\n**Extensão das frases — 20%**\n\nA média de eojeol por frase é usada como um indicador adicional de complexidade estrutural.\n\n**Classificação final**\n\nOs três componentes são combinados na pontuação HanLevel. Os limites provisórios são:\n\n- **Iniciante:** abaixo de 25\n- **Intermediário:** de 25 a menos de 50\n- **Avançado:** 50 ou mais\n\nEsses limites foram calibrados em um pequeno conjunto interno de desenvolvimento. Não correspondem a limites oficiais do TOPIK ou do CEFR.\n\nO HanLevel utiliza um modelo baseado em regras para tornar sua estimativa de dificuldade transparente e verificável.\n'

_translation_pattern = re.compile("|".join((r"\b" + re.escape(k) + r"\b") if k in {"low", "moderate", "high", "beginner", "intermediate", "advanced"} else re.escape(k) for k in sorted(TRANSLATIONS, key=len, reverse=True)))

def tr(value):
    if language != "Português" or not isinstance(value, str):
        return value
    return _translation_pattern.sub(lambda match: TRANSLATIONS[match.group(0)], value)

TRANSLATIONS["Hi ^^ I'm Mongle (몽글), your HanLevel Tutor."] = "Oi ^^ Sou Mongle (몽글), seu Tutor HanLevel."
_translation_pattern = re.compile("|".join((r"\b" + re.escape(k) + r"\b") if k in {"low", "moderate", "high", "beginner", "intermediate", "advanced"} else re.escape(k) for k in sorted(TRANSLATIONS, key=len, reverse=True)))

SPANISH_TRANSLATIONS = {
'Korean Readability Profiler':'Analizador de legibilidad del coreano',
'Korean Readability Profiler · AI Tutor':'Analizador de legibilidad del coreano · Tutor de IA',
'Know if a Korean text is right for your level':'Descubre si un texto en coreano es adecuado para tu nivel',
' — and understand why. ':' — y entiende por qué. ',
'HanLevel analyzes vocabulary, grammar, and sentence length to estimate how challenging a Korean text may be.':'HanLevel analiza el vocabulario, la gramática y la longitud de las oraciones para estimar la dificultad de un texto en coreano.',
'Korean text':'Texto en coreano','Analyze difficulty':'Analizar dificultad','Tell Lívia':'Cuéntale a Lívia',
'Please enter some Korean text first.':'Primero escribe un texto en coreano.','Analyzing Korean text...':'Analizando el texto en coreano...',
'Estimated difficulty':'Dificultad estimada','Estimated level':'Nivel estimado','HanLevel score:':'Puntuación HanLevel:',
'Readability profile':'Perfil de legibilidad','Vocabulary difficulty':'Dificultad del vocabulario','Grammar complexity':'Complejidad gramatical','Sentence length':'Longitud de las oraciones','Vocabulary':'Vocabulario','Grammar':'Gramática',
'Beginner':'Principiante','Intermediate':'Intermedio','Advanced':'Avanzado','Unclassified':'Sin clasificar',
'Higher scores indicate greater estimated difficulty.':'Las puntuaciones más altas indican mayor dificultad estimada.',
'Contribution to HanLevel score':'Contribución a la puntuación HanLevel',' points':' puntos',
'Weighted contributions add up to the final HanLevel score.':'Las contribuciones ponderadas suman la puntuación final de HanLevel.',
'See analysis details':'Ver detalles del análisis','Dictionary coverage:':'Cobertura del diccionario:',
'Average eojeol per sentence:':'Promedio de eojeol por oración:','Vocabulary profile':'Perfil del vocabulario',
'Potentially challenging vocabulary':'Vocabulario potencialmente difícil','Detected structural markers':'Marcadores estructurales identificados',
'Counts include repeated lexical items. The challenging-vocabulary list below shows each word only once.':'El recuento incluye elementos léxicos repetidos. La lista siguiente muestra cada palabra una sola vez.',
'No intermediate or advanced vocabulary was identified in the graded dictionary entries.':'No se identificó vocabulario intermedio o avanzado en las entradas clasificadas del diccionario.',
'HanLevel detected ':'HanLevel identificó ',' structural markers in total.':' marcadores estructurales en total.',
'No weighted structural markers were detected.':'No se identificaron marcadores estructurales ponderados.',
'These markers are used by HanLevel\'s rule-based grammar-complexity component. They are structural indicators, not official learner-level grammar classifications.':'Estos marcadores se utilizan en el componente de complejidad gramatical basado en reglas de HanLevel. Son indicadores estructurales, no clasificaciones oficiales del nivel gramatical.',
'How HanLevel calculates difficulty':'Cómo calcula HanLevel la dificultad',
'Ask Mongle (몽글)':'Habla con Mongle (몽글)','Suggested questions':'Preguntas sugeridas',
'What does this text mean?':'¿Qué significa este texto?','Explain the grammar':'Explica la gramática',
'Which words are difficult?':'¿Qué palabras son difíciles?','Make it easier':'Simplifica el texto','Make it more advanced':'Haz el texto más avanzado',
'Why is this ':'¿Por qué este texto es ','Why ':'¿Por qué ',
'Conversation':'Conversación','Ask me anything about this text':'Pregunta sobre este texto',
'e.g. Why is -는데 used here? Is there an easier word for this?':'Ej.: ¿Por qué se usa -는데 aquí? ¿Hay una palabra más sencilla?',
'Send':'Enviar','thinking...':'pensando...',
'Hi ^^ I’m Mongle (몽글), your HanLevel Tutor. Pick a question above or type your own below. I\'ll stay focused on this text with you ^^':'Hola ^^ Soy Mongle (몽글), tu Tutor HanLevel. Elige una pregunta arriba o escribe la tuya abajo. Exploremos este texto juntos ^^',
'I couldn\'t finish that answer just now. Try me again in a moment? ^^':'No pude terminar la respuesta. ¿Puedes intentarlo de nuevo en un momento? ^^',
'Found something wrong with the tutor?':'¿Encontraste algún problema con el tutor?','let us know':'Avísanos',
'Hi ^^ I\'m the HanLevel Tutor.':'Hola ^^ Soy Mongle (몽글), tu Tutor HanLevel.',
'Hi ^^ I\'m Mongle (몽글), your HanLevel Tutor.':'Hola ^^ Soy Mongle (몽글), tu Tutor HanLevel.',
'This is my creator,':'Mi creadora es',
'If I gave you an inaccurate explanation, hallucinated something,\n        or just acted a little weird, please tell her. It helps us make\n        this tutor better :)':'Si di una explicación incorrecta, inventé alguna información\n        o me comporté de forma extraña, avísale. Nos ayuda a\n        mejorar este tutor :)',
'Email Lívia:':'Escríbele a Lívia:',
'The private contact email has not been configured yet.':'El correo de contacto todavía no está configurado.',
'Technical details':'Detalles técnicos',
'Ask about meaning, vocabulary, grammar, or how this\n                        Korean could be expressed differently. I\'m here to\n                        explore the text with you ^^':'Pregunta sobre el significado, el vocabulario, la gramática u otras\n                        formas de expresar este texto en coreano. Vamos a\n                        explorar el texto juntos ^^',
'The readability analysis works without AI, but the tutor needs GEMINI_API_KEY configured in this deployment.':'El análisis de legibilidad funciona sin IA, pero el tutor no está disponible con esta configuración.',
'The text has ':'El texto presenta ',' vocabulary difficulty, ':' dificultad de vocabulario, ',
' grammatical complexity, and ':' complejidad gramatical y ',' sentence-length difficulty. ':' dificultad relacionada con la longitud de las oraciones. ',
' contributes the most to the final score (+':' es el factor que más contribuye a la puntuación final (+',
'Most classified lexical items are ':'La mayoría de los elementos léxicos clasificados pertenecen al nivel ',
' level. ':' . ','Sentences average ':'Las oraciones tienen un promedio de ',' eojeol.':' eojeol.',
'low':'baja','moderate':'moderada','high':'alta','beginner':'principiante','intermediate':'intermedio','advanced':'avanzado',
'Vocabulary coverage is limited, so the lexical estimate should be interpreted cautiously.':'La cobertura del vocabulario es limitada; interpreta la estimación léxica con cautela.',
'Limited vocabulary coverage (':'Cobertura limitada del vocabulario (',
'The difficulty estimate may be less reliable because many lexical items could not be assigned a learner level.':'La estimación puede ser menos fiable porque no se pudo asignar un nivel a muchos elementos léxicos.',
'Prefinal ending':'Terminación prefinal','Connective ending':'Terminación conectiva','Adnominal ending':'Terminación adnominal','Nominalizing ending':'Terminación nominalizadora','Auxiliary verb':'Verbo auxiliar','Quotation particle':'Partícula de cita','Structural marker':'Marcador estructural',
}

SPANISH_TRANSLATIONS["\nHanLevel combines three interpretable indicators:\n\n**Vocabulary difficulty — 45%**\n\nVocabulary is matched against learner-level information from the Korean Learners' Dictionary (한국어기초사전).\n\nBeginner entries receive a lower difficulty value, while intermediate and advanced entries contribute progressively more to the vocabulary score. Unclassified items do not automatically count as difficult.\n\n**Grammar & morphology — 35%**\n\nKorean morphological analysis is performed with Kiwi. Selected structural markers and morphological density contribute to the grammar-complexity score.\n\nThe grammar score represents structural complexity. It should not be interpreted as an official grammar proficiency level.\n\n**Sentence length — 20%**\n\nAverage eojeol per sentence is used as an additional structural-complexity indicator.\n\n**Final classification**\n\nThe three components are combined into the HanLevel score.\n\nCurrent provisional thresholds are:\n\n- **Beginner:** below 25\n- **Intermediate:** 25 to below 50\n- **Advanced:** 50 and above\n\nThese thresholds were calibrated on a small internally constructed development set. They are not official TOPIK or CEFR boundaries.\n\nHanLevel v0.1 uses a rule-based model designed to make its difficulty estimate transparent and inspectable.\n"] = '\nHanLevel combina tres indicadores interpretables:\n\n**Dificultad del vocabulario — 45%**\n\nEl vocabulario se compara con los niveles del Diccionario de Coreano para Aprendices (한국어기초사전). Las entradas de nivel principiante reciben valores menores; las de nivel intermedio y avanzado contribuyen progresivamente más. Los elementos sin clasificar no se consideran difíciles automáticamente.\n\n**Gramática y morfología — 35%**\n\nKiwi realiza el análisis morfológico del coreano. Los marcadores estructurales seleccionados y la densidad morfológica contribuyen a la complejidad gramatical. Esta puntuación representa complejidad estructural, no un nivel oficial de competencia gramatical.\n\n**Longitud de las oraciones — 20%**\n\nEl promedio de eojeol por oración se usa como indicador adicional de complejidad estructural.\n\n**Clasificación final**\n\nLos tres componentes se combinan en la puntuación HanLevel. Los límites provisionales son:\n\n- **Principiante:** menos de 25\n- **Intermedio:** de 25 a menos de 50\n- **Avanzado:** 50 o más\n\nEstos límites se calibraron con un pequeño conjunto interno de desarrollo. No son límites oficiales de TOPIK ni del MCER.\n\nHanLevel utiliza un modelo basado en reglas para que su estimación de dificultad sea transparente y verificable.\n'

_translation_patterns = {}
for _locale, _dictionary in {"Português": TRANSLATIONS, "Español": SPANISH_TRANSLATIONS}.items():
    _translation_patterns[_locale] = re.compile("|".join((r"\b" + re.escape(k) + r"\b") if k in {"low", "moderate", "high", "beginner", "intermediate", "advanced"} else re.escape(k) for k in sorted(_dictionary, key=len, reverse=True)))

def tr(value):
    if not isinstance(value, str) or language == "English":
        return value
    dictionary = SPANISH_TRANSLATIONS if language == "Español" else TRANSLATIONS
    return _translation_patterns[language].sub(lambda match: dictionary[match.group(0)], value)

class LocalizedUI:
    """Translate presentation strings while preserving analyzer keys and AI output."""
    def __getattr__(self, name):
        method = getattr(st, name)
        def render(*args, **kwargs):
            args = tuple(tr(v) if isinstance(v, str) else v for v in args)
            for key in ("label", "placeholder", "help"):
                if key in kwargs:
                    kwargs[key] = tr(kwargs[key])
            return method(*args, **kwargs)
        return render

ui = LocalizedUI()

# STYLING
# =========================================================

ui.markdown(
    """
<style>

/* ---------- STREAMLIT ---------- */

[data-testid="stHeader"] {
    display: none;
}

[data-testid="stDecoration"] {
    display: none;
}


/* ---------- PAGE ---------- */

.stApp {
    background:
        radial-gradient(
            circle at top left,
            #eef7ff 0%,
            transparent 35%
        ),
        radial-gradient(
            circle at top right,
            #fff0f4 0%,
            transparent 35%
        ),
        #fbfcff;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* =========================================================
   HERO
   ========================================================= */

.hero-card {
    position: relative;
    overflow: hidden;

    padding: 2.6rem 2.5rem;

    margin-bottom: 2rem;

    border-radius: 28px;

    border:
        1px solid
        rgba(210, 220, 240, 0.85);

    background:
        linear-gradient(
            135deg,
            rgba(238, 247, 255, 0.96),
            rgba(250, 245, 255, 0.96),
            rgba(255, 240, 244, 0.92)
        );

    box-shadow:
        0 14px 40px
        rgba(50, 65, 100, 0.08);

    text-align: center;
}


/* decorative circles */

.hero-card::before {
    content: "";

    position: absolute;

    width: 190px;
    height: 190px;

    border-radius: 50%;

    background:
        rgba(159, 220, 247, 0.25);

    top: -100px;
    right: -55px;
}

.hero-card::after {
    content: "";

    position: absolute;

    width: 150px;
    height: 150px;

    border-radius: 50%;

    background:
        rgba(243, 171, 196, 0.20);

    bottom: -85px;
    left: -35px;
}


.hero-content {
    position: relative;
    z-index: 2;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;
}


.hero-badge {
    display: inline-block;

    padding: 6px 11px;

    border-radius: 999px;

    background:
        rgba(255, 255, 255, 0.78);

    border:
        1px solid
        rgba(190, 200, 225, 0.8);

    color: #65708a;

    font-size: 0.75rem;
    font-weight: 700;

    letter-spacing: 0.07em;

    text-transform: uppercase;

    margin-bottom: 1rem;
}


.hero-title {
    font-size: 3.8rem;
    font-weight: 850;

    letter-spacing: -2px;

    color: #172033;

    line-height: 1;

    margin-bottom: 0.9rem;
}


.hero-description {
    max-width: 650px;

    margin-left: auto;
    margin-right: auto;

    color: #58657c;

    font-size: 1.05rem;
    line-height: 1.65;

    margin-bottom: 1.4rem;
}


.hero-highlight {
    color: #536dcc;
    font-weight: 700;
}


.hero-chips {
    display: flex;
    flex-wrap: wrap;

    justify-content: center;
    align-items: center;

    gap: 0.6rem;

    width: 100%;
}


.hero-chip {
    padding: 7px 13px;

    border-radius: 999px;

    background:
        rgba(255, 255, 255, 0.78);

    border:
        1px solid
        rgba(215, 222, 238, 0.9);

    color: #556078;

    font-size: 0.82rem;
    font-weight: 600;
}


/* ---------- TEXT AREA ---------- */

.stTextArea textarea {
    background-color: white;

    border:
        1.5px solid #d9e2f0;

    border-radius: 16px;

    padding: 16px;

    color: #172033;
}

.stTextArea textarea:focus {
    border-color: #7c9ee8;

    box-shadow:
        0 0 0 2px
        rgba(124, 158, 232, 0.15);
}


/* ---------- BUTTON ---------- */

.stButton > button {
    border-radius: 14px;

    font-weight: 700;

    height: 3rem;

    border: none;

    background:
        linear-gradient(
            90deg,
            #6587dd,
            #8f79d8
        );

    color: white;
}

.stButton > button:hover {
    border: none;

    color: white;

    transform:
        translateY(-1px);
}


/* ---------- RESULT CARD ---------- */

.level-card {
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.98),
            rgba(248, 249, 255, 0.98)
        );

    padding: 1.8rem;

    border-radius: 22px;

    border:
        1px solid #e2e8f0;

    margin-top: 1rem;
    margin-bottom: 1rem;

    box-shadow:
        0 8px 30px
        rgba(40, 55, 90, 0.07);

    text-align: center;

    overflow: hidden;
}


.level-kicker {
    font-size: 0.78rem;

    font-weight: 700;

    letter-spacing: 0.08em;

    text-transform: uppercase;

    color: #94a3b8;

    margin-bottom: 6px;
}


.level-name {
    font-size: 2.4rem;

    font-weight: 800;
}


.score-text {
    color: #64748b;

    font-size: 1rem;

    margin-top: 4px;
}


/* ---------- DIFFICULTY SCALE ---------- */

.difficulty-wrapper {
    margin-top: 1.8rem;
    margin-bottom: 2rem;

    padding-top: 1.8rem;
}


.difficulty-track {
    position: relative;

    width: 100%;
    height: 16px;

    border-radius: 999px;

    box-shadow:
        inset 0 1px 3px
        rgba(35, 48, 80, 0.10),

        0 3px 12px
        rgba(55, 70, 110, 0.10);
}


/* colored zones */

.difficulty-segment {
    position: absolute;

    top: 0;

    height: 100%;
}


.segment-beginner {
    left: 0;

    width: 25%;

    background-color: #9fdcf7;

    border-radius:
        999px 0 0 999px;
}


.segment-intermediate {
    left: 25%;

    width: 25%;

    background-color: #c3a9e7;
}


.segment-advanced {
    left: 50%;

    width: 50%;

    background-color: #f3abc4;

    border-radius:
        0 999px 999px 0;
}


/* threshold separators */

.difficulty-threshold {
    position: absolute;

    top: -3px;

    width: 2px;
    height: 22px;

    background:
        rgba(255, 255, 255, 0.65);

    border-radius: 2px;

    z-index: 3;
}


.threshold-one {
    left: 25%;
}


.threshold-two {
    left: 50%;
}


/* score marker */

.difficulty-marker {
    position: absolute;

    top: 50%;

    width: 28px;
    height: 28px;

    transform:
        translate(-50%, -50%);

    border-radius: 50%;

    background: white;

    border:
        6px solid #786ed7;

    box-shadow:
        0 4px 14px
        rgba(57, 67, 120, 0.22);

    z-index: 5;
}


/* score bubble */

.difficulty-score {
    position: absolute;

    bottom: 25px;

    transform:
        translateX(-50%);

    background: #172033;

    color: white;

    padding: 4px 9px;

    border-radius: 999px;

    font-size: 0.78rem;
    font-weight: 700;

    white-space: nowrap;

    z-index: 6;
}


/* scale labels */

.difficulty-labels {
    display: grid;

    grid-template-columns:
        1fr 1fr 2fr;

    margin-top: 12px;

    color: #64748b;

    font-size: 0.85rem;
    font-weight: 600;

    text-align: center;
}


/* ---------- EXPLANATION ---------- */

.reason-box {
    padding:
        1.2rem 1.4rem;

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            #f1f6ff,
            #faf5ff
        );

    border:
        1px solid #dde5f4;

    margin-top: 1.2rem;
    margin-bottom: 2rem;

    color: #263248;
}


/* ---------- METRICS ---------- */

[data-testid="stMetric"] {
    background-color: white;

    border:
        1px solid #e2e8f0;

    padding: 18px;

    border-radius: 18px;

    box-shadow:
        0 5px 20px
        rgba(40, 55, 90, 0.05);
}


/* ---------- EXPANDERS ---------- */

[data-testid="stExpander"] {
    background-color:
        rgba(255, 255, 255, 0.75);

    border:
        1px solid #e3e8f2;

    border-radius: 14px;
}


/* ---------- GENERAL ---------- */

h1,
h2,
h3 {
    color: #172033;
}

hr {
    border-color: #e8edf5;
}


/* ---------- RESPONSIVE ---------- */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;

        padding-top: 1.2rem;
    }

    .hero-card {
        padding:
            2rem 1.4rem;
    }

    .hero-title {
        font-size: 2.9rem;
    }

    .hero-description {
        font-size: 0.95rem;
    }

    .hero-chip {
        font-size: 0.76rem;
    }

    .level-name {
        font-size: 2rem;
    }

    .difficulty-labels {
        font-size: 0.75rem;
    }

    [data-testid="stMetric"] {
        padding: 14px;
    }
}

/* ---------- AI TUTOR ---------- */

.tutor-shell {
    margin-top: 1.2rem;
    padding: 1.4rem;
    border-radius: 22px;
    border: 1px solid #dedff2;
    background:
        linear-gradient(
            135deg,
            rgba(247, 245, 255, 0.98),
            rgba(241, 248, 255, 0.98)
        );
    box-shadow: 0 8px 28px rgba(56, 62, 110, 0.07);
}

.tutor-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 0.35rem;
}

.tutor-pet {
    position: relative;
    width: 48px;
    height: 40px;
    flex: 0 0 auto;
    border-radius: 52% 48% 46% 54% / 58% 52% 48% 42%;
    background: #7464c9;
    box-shadow: 0 5px 14px rgba(85, 72, 160, 0.22);
}

.tutor-pet::before,
.tutor-pet::after {
    content: "";
    position: absolute;
    top: 13px;
    width: 5px;
    height: 7px;
    border-radius: 50%;
    background: #ffffff;
}

.tutor-pet::before {
    left: 13px;
}

.tutor-pet::after {
    right: 13px;
}

.tutor-title {
    color: #172033;
    font-size: 1.25rem;
    font-weight: 800;
}

.tutor-subtitle {
    color: #68738b;
    font-size: 0.9rem;
    line-height: 1.45;
}

[data-testid="stChatMessage"] {
    border-radius: 16px;
}

.typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    min-height: 24px;
    padding: 2px 0;
    white-space: nowrap;
}

.typing-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    border-radius: 50%;
    background: #786ed7;
    opacity: 0.35;
    animation: hanlevelTyping 1.15s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.16s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.32s;
}

@keyframes hanlevelTyping {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.35;
    }
    30% {
        transform: translateY(-4px);
        opacity: 1;
    }
}

.tutor-thinking-label {
    display: inline-block;
    width: auto;
    height: auto;
    margin-left: 8px;
    color: #7a8296;
    font-size: 0.84rem;
    line-height: 1.2;
}

.tutor-dialog-pet-wrap {
    display: flex;
    justify-content: center;
    margin: 0.4rem 0 1rem 0;
}

.tutor-dialog-pet {
    position: relative;
    width: 76px;
    height: 62px;
    border-radius: 52% 48% 46% 54% / 58% 52% 48% 42%;
    background: #7464c9;
    box-shadow: 0 8px 22px rgba(85, 72, 160, 0.24);
}

.tutor-dialog-pet::before,
.tutor-dialog-pet::after {
    content: "";
    position: absolute;
    top: 21px;
    width: 7px;
    height: 10px;
    border-radius: 50%;
    background: #ffffff;
}

.tutor-dialog-pet::before {
    left: 21px;
}

.tutor-dialog-pet::after {
    right: 21px;
}

.feedback-note {
    text-align: center;
    color: #8a91a5;
    font-size: 0.78rem;
    margin-top: 0.4rem;
}

/* Refined original blob: softly sculpted silhouette, bright eyes, quiet expression. */
.tutor-pet,.tutor-dialog-pet{width:56px;height:48px;border-radius:48% 52% 36% 38% / 60% 58% 36% 35%;background:radial-gradient(ellipse at 28% 18%,#b9a0f0 0%,#9675dd 24%,#7951bd 65%,#603a9e 100%);border:2px solid #6842a6;box-shadow:inset 0 3px 1px #d2bbff70,inset 0 -5px 0 #4b287f25,0 5px 0 -2px #4d307d22;transform:rotate(-3deg)}
.tutor-pet:before,.tutor-pet:after{top:17px;width:8px;height:11px;background:#fff9ff;border-radius:50%;box-shadow:0 1px 0 #45217155;animation:blob-blink 7s infinite}
.tutor-pet:before{left:15px}.tutor-pet:after{right:13px}
.tutor-pet .tutor-expression{position:absolute;left:25px;top:30px;width:7px;height:4px;border:solid #4e297f;border-width:0 0 2px;border-radius:0 0 60% 60%}
.tutor-pet .tutor-expression:before,.tutor-pet .tutor-expression:after{content:'';position:absolute;top:-6px;width:7px;height:3px;border-radius:50%;background:#efb7db60}
.tutor-pet .tutor-expression:before{left:-15px}.tutor-pet .tutor-expression:after{left:12px}
@keyframes blob-blink{0%,43%,47%,100%{transform:scaleY(1)}45%{transform:scaleY(.12)}}
.tutor-dialog-pet{width:84px;height:72px;margin:8px auto 24px;box-shadow:inset 0 4px 1px #d2bbff70,inset 0 -7px 0 #4b287f25,0 7px 0 -2px #4d307d22}
.tutor-dialog-pet:before,.tutor-dialog-pet:after{top:25px;width:11px;height:15px}.tutor-dialog-pet:before{left:24px}.tutor-dialog-pet:after{right:22px}.tutor-dialog-pet .tutor-expression{left:38px;top:44px;width:9px;height:5px}.tutor-dialog-pet .tutor-expression:before{left:-22px;width:10px}.tutor-dialog-pet .tutor-expression:after{left:19px;width:10px}

.tutor-dialog-pet{width:56px;height:48px;transform:scale(1.4) rotate(-3deg);margin:20px auto}
.st-key-hanlevel_tutor .stButton > button{background:#faf9ff;color:#615388;border:1px solid #e0dbef;border-radius:22px;height:auto;min-height:2.7rem;font-size:.875rem}
.st-key-hanlevel_tutor .stButton > button:hover{background:#eee8fc;transform:none}
.st-key-hanlevel_tutor [data-testid="stChatMessage"]{background:#f7f6fc;border-radius:16px}
.typing-indicator{display:flex;align-items:center;gap:.4rem;width:max-content;max-width:100%}
.tutor-thinking-label{white-space:nowrap;word-break:normal;flex-shrink:0}
@media(prefers-reduced-motion:reduce){.tutor-pet:before,.tutor-pet:after{animation:none}}

/* Compact language menu in the top-right corner. */
.st-key-language_switch {
    display: flex;
    align-items: flex-end;
    margin-bottom: .5rem;
}
.st-key-language_switch > div {
    width: 100%;
}
.st-key-language_switch [data-testid="stSelectbox"] {
    width: 142px;
    max-width: 100%;
    margin-left: auto;
}
.st-key-language_switch [data-baseweb="select"] > div {
    min-height: 34px;
    font-size: .875rem;
    border-radius: 10px;
    background: rgba(255,255,255,.85);
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# CONSTANTS
# =========================================================

LOW_COVERAGE_THRESHOLD = 60.0


GRAMMAR_TAG_LABELS = {
    "EP": "Prefinal ending",
    "EC": "Connective ending",
    "ETM": "Adnominal ending",
    "ETN": "Nominalizing ending",
    "VX": "Auxiliary verb",
    "JKQ": "Quotation particle",
}


# =========================================================
# SESSION STATE
# =========================================================

if "source_text" not in st.session_state:
    st.session_state.source_text = None

if "source_analysis" not in st.session_state:
    st.session_state.source_analysis = None

if "tutor_history" not in st.session_state:
    st.session_state.tutor_history = []


def get_gemini_api_key():

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


def get_contact_email():

    email = os.getenv("CONTACT_EMAIL")

    if email:
        return email

    try:
        return st.secrets["CONTACT_EMAIL"]
    except (KeyError, FileNotFoundError):
        return None


@ui.dialog("Tell Lívia")
def show_tutor_contact():

    ui.markdown(
        """
        <div class="tutor-dialog-pet-wrap">
            <div class="tutor-dialog-pet"><span class="tutor-expression"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ui.markdown(
        """
        **Hi ^^ I'm Mongle (몽글), your HanLevel Tutor.**

        This is my creator, **Lívia**.

        If I gave you an inaccurate explanation, hallucinated something,
        or just acted a little weird, please tell her. It helps us make
        this tutor better :)
        """
    )

    contact_email = get_contact_email()

    if contact_email:

        ui.markdown(
            f"**Email Lívia:** [{contact_email}](mailto:{contact_email})"
        )

    else:

        ui.caption(
            "The private contact email has not been configured yet."
        )


# =========================================================
# HELPERS
# =========================================================

def safe_score(value):

    if value is None:
        return 0.0

    return value


def describe_score(score):

    if score < 25:
        return "low"

    if score < 50:
        return "moderate"

    return "high"


# ---------------------------------------------------------
# Weighted contribution
# ---------------------------------------------------------

def calculate_contributions(result):

    vocabulary_score = (
        result["vocabulary"][
            "vocabulary_score"
        ]
    )

    grammar_score = (
        result["grammar"][
            "grammar_score"
        ]
    )

    sentence_score = (
        result["sentence_length"][
            "sentence_length_score"
        ]
    )

    components = []

    if vocabulary_score is not None:

        components.append(
            (
                "Vocabulary",
                vocabulary_score,
                0.45,
            )
        )

    components.append(
        (
            "Grammar",
            grammar_score,
            0.35,
        )
    )

    components.append(
        (
            "Sentence length",
            sentence_score,
            0.20,
        )
    )

    total_weight = sum(
        weight
        for _, _, weight
        in components
    )

    contributions = {}

    for name, score, weight in components:

        contributions[name] = (
            score
            * weight
            / total_weight
        )

    return contributions


# ---------------------------------------------------------
# Vocabulary profile
# ---------------------------------------------------------

def get_vocabulary_profile(result):

    profile = {
        "Beginner": 0,
        "Intermediate": 0,
        "Advanced": 0,
        "Unclassified": 0,
    }

    words = (
        result["vocabulary"][
            "words"
        ]
    )

    for item in words:

        grade = item["grade"]

        if grade == "초급":

            profile["Beginner"] += 1

        elif grade == "중급":

            profile["Intermediate"] += 1

        elif grade == "고급":

            profile["Advanced"] += 1

        else:

            profile["Unclassified"] += 1

    return profile


def get_dominant_vocabulary_level(
    profile
):

    classified = {
        "Beginner":
            profile["Beginner"],

        "Intermediate":
            profile["Intermediate"],

        "Advanced":
            profile["Advanced"],
    }

    if sum(
        classified.values()
    ) == 0:

        return None

    return max(
        classified,
        key=classified.get,
    )


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

def generate_explanation(result):

    vocab_score = safe_score(
        result["vocabulary"][
            "vocabulary_score"
        ]
    )

    grammar_score = (
        result["grammar"][
            "grammar_score"
        ]
    )

    sentence_score = (
        result["sentence_length"][
            "sentence_length_score"
        ]
    )

    average_eojeol = (
        result["sentence_length"][
            "average_eojeol"
        ]
    )

    coverage = (
        result["vocabulary"][
            "coverage"
        ]
    )

    contributions = (
        calculate_contributions(
            result
        )
    )

    strongest = max(
        contributions,
        key=contributions.get,
    )

    profile = (
        get_vocabulary_profile(
            result
        )
    )

    dominant_vocab = (
        get_dominant_vocabulary_level(
            profile
        )
    )

    vocab_description = (
        describe_score(
            vocab_score
        )
    )

    grammar_description = (
        describe_score(
            grammar_score
        )
    )

    sentence_description = (
        describe_score(
            sentence_score
        )
    )

    explanation = (
        f"The text has "
        f"{vocab_description} vocabulary difficulty, "
        f"{grammar_description} grammatical complexity, "
        f"and {sentence_description} "
        f"sentence-length difficulty. "
    )

    explanation += (
        f"{strongest} contributes the most "
        f"to the final score "
        f"(+{contributions[strongest]:.1f} points). "
    )

    if dominant_vocab is not None:

        explanation += (
            f"Most classified lexical items are "
            f"{dominant_vocab.lower()} level. "
        )

    explanation += (
        f"Sentences average "
        f"{average_eojeol:.1f} eojeol."
    )

    if (
        coverage
        < LOW_COVERAGE_THRESHOLD
    ):

        explanation += (
            " Vocabulary coverage is limited, "
            "so the lexical estimate should be "
            "interpreted cautiously."
        )

    return explanation


# ---------------------------------------------------------
# Challenging vocabulary
# ---------------------------------------------------------

def get_difficult_words(result):

    words = (
        result["vocabulary"][
            "words"
        ]
    )

    difficult = []

    seen = set()

    for item in words:

        word = item["word"]
        grade = item["grade"]

        if grade not in {
            "중급",
            "고급",
        }:

            continue

        key = (
            word,
            grade,
        )

        if key in seen:

            continue

        seen.add(key)

        difficult.append(
            {
                "word": word,
                "grade": grade,
            }
        )

    return difficult


# ---------------------------------------------------------
# Grammar structures
# ---------------------------------------------------------

def format_grammar_structure(
    item
):

    form = None
    tag = None

    if isinstance(
        item,
        dict
    ):

        form = (
            item.get("form")
            or item.get("word")
            or item.get("lemma")
        )

        tag = (
            item.get("tag")
            or item.get("pos")
        )

    else:

        form = getattr(
            item,
            "form",
            None,
        )

        tag = getattr(
            item,
            "tag",
            None,
        )

        if form is None:

            form = str(item)

    if not form:

        form = "Unknown"

    display_form = form

    if (
        tag
        and tag.startswith("E")
        and not form.startswith("-")
    ):

        display_form = (
            f"-{form}"
        )

    display_normalization = {

        ("ᆫ", "ETM"):
            "-(으)ㄴ",

        ("ㄴ", "ETM"):
            "-(으)ㄴ",

        ("ᆯ", "ETM"):
            "-(으)ㄹ",

        ("ㄹ", "ETM"):
            "-(으)ㄹ",

        ("있", "VX"):
            "있다",

        ("않", "VX"):
            "않다",
    }

    display_form = (
        display_normalization.get(
            (
                form,
                tag,
            ),
            display_form,
        )
    )

    label = (
        GRAMMAR_TAG_LABELS.get(
            tag,
            tag or "Structural marker",
        )
    )

    return (
        display_form,
        tag,
        label,
    )


def get_unique_grammar_structures(
    result
):

    structures = (
        result["grammar"][
            "structures"
        ]
    )

    unique = []

    seen = set()

    for item in structures:

        form, tag, label = (
            format_grammar_structure(
                item
            )
        )

        key = (
            form,
            tag,
        )

        if key in seen:

            continue

        seen.add(key)

        unique.append(
            {
                "form": form,
                "tag": tag,
                "label": label,
            }
        )

    return unique


# =========================================================
# HERO
# =========================================================

hero_html = (
    '<div class="hero-card">'

        '<div class="hero-content">'

            '<div class="hero-badge">'
                'Korean Readability Profiler · AI Tutor'
            '</div>'

            '<div class="hero-title">'
                'HanLevel'
            '</div>'

            '<div class="hero-description">'

                '<span class="hero-highlight">'
                    'Know if a Korean text is right for your level'
                '</span>'

                ' — and understand why. '

                'HanLevel analyzes vocabulary, grammar, '
                'and sentence length to estimate how challenging '
                'a Korean text may be.'

            '</div>'

            '<div class="hero-chips">'

                '<span class="hero-chip">'
                    'Vocabulary · 45%'
                '</span>'

                '<span class="hero-chip">'
                    'Grammar · 35%'
                '</span>'

                '<span class="hero-chip">'
                    'Sentence length · 20%'
                '</span>'

            '</div>'

        '</div>'

    '</div>'
)


ui.markdown(
    hero_html,
    unsafe_allow_html=True,
)


# =========================================================
# INPUT
# =========================================================

text = ui.text_area(
    "Korean text",

    height=180,
    key="korean_source_input",

    placeholder=(
        "예: 오늘은 날씨가 정말 좋네요. "
        "친구와 함께 공원에 갔어요."
    ),
)


analyze_button = ui.button(
    "Analyze difficulty",
    key="analyze_difficulty",

    type="primary",

    use_container_width=True,
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if not text.strip():

        ui.warning(
            "Please enter some Korean text first."
        )

    else:

        with ui.spinner(
            "Analyzing Korean text..."
        ):

            analyzed_text = text.strip()
            analyzed_result = analyze_text(analyzed_text)

        st.session_state.source_text = analyzed_text
        st.session_state.source_analysis = analyzed_result
        st.session_state.tutor_history = []


if st.session_state.source_analysis is not None:

    text = st.session_state.source_text
    result = st.session_state.source_analysis

    # -------------------------------------------------
    # Extract results
    # -------------------------------------------------

    final_score = (
        result["final_score"]
    )

    level = (
        result["level"]
    )

    vocab_score = safe_score(
        result["vocabulary"][
            "vocabulary_score"
        ]
    )

    grammar_score = (
        result["grammar"][
            "grammar_score"
        ]
    )

    sentence_score = (
        result["sentence_length"][
            "sentence_length_score"
        ]
    )

    coverage = (
        result["vocabulary"][
            "coverage"
        ]
    )

    average_eojeol = (
        result["sentence_length"][
            "average_eojeol"
        ]
    )

    explanation = (
        generate_explanation(
            result
        )
    )

    difficult_words = (
        get_difficult_words(
            result
        )
    )

    vocabulary_profile = (
        get_vocabulary_profile(
            result
        )
    )

    contributions = (
        calculate_contributions(
            result
        )
    )

    grammar_structures = (
        get_unique_grammar_structures(
            result
        )
    )


    # -------------------------------------------------
    # Colors
    # -------------------------------------------------

    level_colors = {

        "Beginner":
            "#62a9d8",

        "Intermediate":
            "#786ed7",

        "Advanced":
            "#d66f9e",
    }

    level_color = (
        level_colors.get(
            level,
            "#786ed7",
        )
    )


    # =================================================
    # MAIN RESULT
    # =================================================

    ui.subheader(
        "Estimated difficulty"
    )


    result_card_html = (
        f'<div class="level-card">'

        f'<div class="level-kicker">'
        f'Estimated level'
        f'</div>'

        f'<div class="level-name" '
        f'style="color:{level_color};">'
        f'{level}'
        f'</div>'

        f'<div class="score-text">'
        f'HanLevel score: '
        f'{final_score:.1f} / 100'
        f'</div>'

        f'</div>'
    )


    ui.markdown(
        result_card_html,
        unsafe_allow_html=True,
    )


    # =================================================
    # DIFFICULTY SCALE
    # =================================================

    marker_position = min(
        max(
            final_score,
            0,
        ),
        100,
    )


    difficulty_html = (
        f'<div class="difficulty-wrapper">'

        f'<div class="difficulty-track">'

        f'<div class="difficulty-segment '
        f'segment-beginner"></div>'

        f'<div class="difficulty-segment '
        f'segment-intermediate"></div>'

        f'<div class="difficulty-segment '
        f'segment-advanced"></div>'

        f'<div class="difficulty-threshold '
        f'threshold-one"></div>'

        f'<div class="difficulty-threshold '
        f'threshold-two"></div>'

        f'<div class="difficulty-score" '
        f'style="left:{marker_position}%;">'
        f'{final_score:.1f}'
        f'</div>'

        f'<div class="difficulty-marker" '
        f'style="left:{marker_position}%; '
        f'border-color:{level_color};">'
        f'</div>'

        f'</div>'

        f'<div class="difficulty-labels">'
        f'<span>Beginner</span>'
        f'<span>Intermediate</span>'
        f'<span>Advanced</span>'
        f'</div>'

        f'</div>'
    )


    ui.markdown(
        difficulty_html,
        unsafe_allow_html=True,
    )


    # =================================================
    # EXPLANATION
    # =================================================

    explanation_html = (
        f'<div class="reason-box">'

        f'<strong>'
        f'Why {level}?'
        f'</strong>'

        f'<br>'

        f'{explanation}'

        f'</div>'
    )


    ui.markdown(
        explanation_html,
        unsafe_allow_html=True,
    )


    # =================================================
    # LOW COVERAGE WARNING
    # =================================================

    if (
        coverage
        < LOW_COVERAGE_THRESHOLD
    ):

        ui.warning(
            f"Limited vocabulary coverage "
            f"({coverage:.1f}%). "
            "The difficulty estimate may be less reliable "
            "because many lexical items could not be "
            "assigned a learner level."
        )


    # =================================================
    # READABILITY PROFILE
    # =================================================

    ui.subheader(
        "Readability profile"
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        ui.metric(
            "Vocabulary difficulty",
            f"{vocab_score:.1f}/100",
        )


    with col2:

        ui.metric(
            "Grammar complexity",
            f"{grammar_score:.1f}/100",
        )


    with col3:

        ui.metric(
            "Sentence length",
            f"{sentence_score:.1f}/100",
        )


    ui.caption(
        "Higher scores indicate greater "
        "estimated difficulty."
    )


    # =================================================
    # CONTRIBUTION BREAKDOWN
    # =================================================

    ui.markdown(
        "#### Contribution to HanLevel score"
    )


    contribution_columns = (
        st.columns(3)
    )


    with contribution_columns[0]:

        ui.metric(
            "Vocabulary",
            (
                f"+"
                f"{contributions.get('Vocabulary', 0):.1f}"
                f" points"
            ),
        )


    with contribution_columns[1]:

        ui.metric(
            "Grammar",
            (
                f"+"
                f"{contributions.get('Grammar', 0):.1f}"
                f" points"
            ),
        )


    with contribution_columns[2]:

        ui.metric(
            "Sentence length",
            (
                f"+"
                f"{contributions.get('Sentence length', 0):.1f}"
                f" points"
            ),
        )


    ui.caption(
        "Weighted contributions add up "
        "to the final HanLevel score."
    )


    # =================================================
    # DETAILS
    # =================================================

    with ui.expander(
        "See analysis details"
    ):

        ui.write(
            f"**Dictionary coverage:** "
            f"{coverage:.1f}%"
        )


        ui.write(
            f"**Average eojeol per sentence:** "
            f"{average_eojeol:.1f}"
        )


        # ---------------------------------------------
        # Vocabulary profile
        # ---------------------------------------------

        ui.markdown(
            "#### Vocabulary profile"
        )


        vocab_cols = (
            st.columns(4)
        )


        with vocab_cols[0]:

            ui.metric(
                "Beginner",
                vocabulary_profile[
                    "Beginner"
                ],
            )


        with vocab_cols[1]:

            ui.metric(
                "Intermediate",
                vocabulary_profile[
                    "Intermediate"
                ],
            )


        with vocab_cols[2]:

            ui.metric(
                "Advanced",
                vocabulary_profile[
                    "Advanced"
                ],
            )


        with vocab_cols[3]:

            ui.metric(
                "Unclassified",
                vocabulary_profile[
                    "Unclassified"
                ],
            )


        ui.caption(
            "Counts include repeated lexical items. "
            "The challenging-vocabulary list below "
            "shows each word only once."
        )


        # ---------------------------------------------
        # Challenging vocabulary
        # ---------------------------------------------

        if difficult_words:

            ui.markdown(
                "#### Potentially challenging vocabulary"
            )


            for item in difficult_words:

                label = (
                    "Intermediate"
                    if item["grade"] == "중급"
                    else "Advanced"
                )

                ui.write(
                    f"- **{item['word']}** "
                    f"— {label}"
                )


        else:

            ui.write(
                "No intermediate or advanced vocabulary "
                "was identified in the graded "
                "dictionary entries."
            )


        # ---------------------------------------------
        # Grammar structures
        # ---------------------------------------------

        ui.markdown(
            "#### Detected structural markers"
        )


        ui.write(
            f"HanLevel detected "
            f"**{len(result['grammar']['structures'])}** "
            f"structural markers in total."
        )


        if grammar_structures:

            for structure in grammar_structures:

                tag_text = (
                    f" ({structure['tag']})"
                    if structure["tag"]
                    else ""
                )

                ui.write(
                    f"- **{structure['form']}** "
                    f"— {structure['label']}"
                    f"{tag_text}"
                )


        else:

            ui.write(
                "No weighted structural markers "
                "were detected."
            )


        ui.caption(
            "These markers are used by HanLevel's "
            "rule-based grammar-complexity component. "
            "They are structural indicators, not official "
            "learner-level grammar classifications."
        )


    # =================================================
    # METHODOLOGY
    # =================================================

    with ui.expander(
        "How HanLevel calculates difficulty"
    ):

        ui.markdown(
            """
HanLevel combines three interpretable indicators:

**Vocabulary difficulty — 45%**

Vocabulary is matched against learner-level information from the Korean Learners' Dictionary (한국어기초사전).

Beginner entries receive a lower difficulty value, while intermediate and advanced entries contribute progressively more to the vocabulary score. Unclassified items do not automatically count as difficult.

**Grammar & morphology — 35%**

Korean morphological analysis is performed with Kiwi. Selected structural markers and morphological density contribute to the grammar-complexity score.

The grammar score represents structural complexity. It should not be interpreted as an official grammar proficiency level.

**Sentence length — 20%**

Average eojeol per sentence is used as an additional structural-complexity indicator.

**Final classification**

The three components are combined into the HanLevel score.

Current provisional thresholds are:

- **Beginner:** below 25
- **Intermediate:** 25 to below 50
- **Advanced:** 50 and above

These thresholds were calibrated on a small internally constructed development set. They are not official TOPIK or CEFR boundaries.

HanLevel v0.1 uses a rule-based model designed to make its difficulty estimate transparent and inspectable.
"""
        )


    # =====================================================
    # AI TUTOR
    # =====================================================

    with st.container(key="hanlevel_tutor"):
        ui.markdown("---")

        ui.markdown(
            """
            <div class="tutor-shell">
                <div class="tutor-header">
                    <div class="tutor-pet"><span class="tutor-expression"></span></div>
                    <div>
                        <div class="tutor-title">Ask Mongle (몽글)</div>
                        <div class="tutor-subtitle">
                            Ask about meaning, vocabulary, grammar, or how this
                            Korean could be expressed differently. I'm here to
                            explore the text with you ^^
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        gemini_api_key = get_gemini_api_key()

        if gemini_api_key is None:
            ui.info(
                "The readability analysis works without AI, but the tutor needs "
                "GEMINI_API_KEY configured in this deployment."
            )

        suggested_questions = [
            (
                "What does this text mean?",
                "What does this text mean? Explain it clearly.",
            ),
            (
                f"Why is this {result['level']}?",
                "Why did we classify this text at this level? "
                "Use the analysis to explain the main reasons.",
            ),
            (
                "Explain the grammar",
                "Explain the most important or difficult grammar in this text "
                "and what it is doing here.",
            ),
            (
                "Which words are difficult?",
                "Which words in this text may be difficult for a learner, "
                "and what do they mean in context?",
            ),
            (
                "Make it easier",
                "Show me one easier, natural way to express this text while "
                "preserving its meaning. Then explain the main changes.",
            ),
            (
                "Make it more advanced",
                "Show me one more advanced, natural way to express this text "
                "while preserving its meaning. Then explain the main changes.",
            ),
        ]

        ui.caption("Suggested questions")

        question_cols = st.columns(2)
        selected_question = None
        selected_question_display = None

        for index, (label, question) in enumerate(suggested_questions):

            with question_cols[index % 2]:

                if ui.button(
                    label,
                    key=f"tutor_suggestion_{index}",
                    use_container_width=True,
                    disabled=(gemini_api_key is None),
                ):
                    # Keep the detailed English prompt for the tutor, but show
                    # the user the localized button text in the chat bubble.
                    selected_question = question
                    selected_question_display = tr(label)

        if "pending_tutor_question" not in st.session_state:
            st.session_state.pending_tutor_question = None

        if "pending_tutor_display" not in st.session_state:
            st.session_state.pending_tutor_display = None

        def build_turns(history):

            turns = []
            current_turn = []

            for message in history:

                if (
                    message["role"] == "user"
                    and current_turn
                ):
                    turns.append(current_turn)
                    current_turn = []

                current_turn.append(message)

            if current_turn:
                turns.append(current_turn)

            return turns

        if selected_question:
            st.session_state.pending_tutor_question = selected_question
            st.session_state.pending_tutor_display = (
                selected_question_display
            )

        pending_question = st.session_state.pending_tutor_question
        pending_display = (
            st.session_state.pending_tutor_display
            or pending_question
        )

        prior_history = list(
            st.session_state.tutor_history
        )

        if pending_question:

            st.session_state.pending_tutor_question = None
            st.session_state.pending_tutor_display = None

            st.session_state.tutor_history.append(
                {
                    "role": "user",
                    "content": pending_display,
                }
            )

        ui.markdown("#### Conversation")

        chat_box = st.container(
            height=430,
            border=True,
        )

        with chat_box:

            turns = build_turns(
                st.session_state.tutor_history
            )

            if not turns:
                ui.caption(
                    "Hi ^^ I’m Mongle (몽글), your HanLevel Tutor. Pick a question above or type your own below. "
                    "I'll stay focused on this text with you ^^"
                )

            for turn_index, turn in enumerate(
                turns
            ):

                for message in turn:

                    with st.chat_message(
                        message["role"],
                        avatar=TUTOR_AVATAR if message["role"] == "assistant" else None,
                    ):
                        st.markdown(
                            message["content"]
                        )

                if (
                    pending_question
                    and turn_index == len(turns) - 1
                    and turn[-1]["role"] == "user"
                ):

                    with st.chat_message(
                        "assistant", avatar=TUTOR_AVATAR,
                    ):

                        typing_placeholder = st.empty()

                        typing_placeholder.markdown(
                            tr("""
                            <div class="typing-indicator">
                                <span class="typing-dot"></span>
                                <span class="typing-dot"></span>
                                <span class="typing-dot"></span>
                                <span class="tutor-thinking-label">thinking...</span>
                            </div>
                            """),
                            unsafe_allow_html=True,
                        )

                if turn_index < len(turns) - 1:
                    st.divider()

            ui.markdown("---")

            with st.form(
                "tutor_question_form",
                clear_on_submit=True,
            ):

                custom_question = ui.text_input(
                    "Ask me anything about this text",
                    placeholder=(
                        "e.g. Why is -는데 used here? "
                        "Is there an easier word for this?"
                    ),
                    disabled=(gemini_api_key is None),
                )

                ask_button = ui.form_submit_button(
                    "Send",
                    use_container_width=True,
                    disabled=(gemini_api_key is None),
                )

            if ask_button and custom_question.strip():

                custom_text = custom_question.strip()

                st.session_state.pending_tutor_question = (
                    custom_text
                )
                st.session_state.pending_tutor_display = (
                    custom_text
                )

                st.rerun()

        if pending_question:

            try:
                tutor_result = ask_tutor(
                    text=st.session_state.source_text,
                    analysis=st.session_state.source_analysis,
                    question=pending_question + ("\nPlease answer in Brazilian Portuguese." if language == "Português" else "\nPlease answer in Spanish." if language == "Español" else "\nPlease answer in English."),
                    history=prior_history,
                    api_key=gemini_api_key,
                )

            except Exception as exc:

                error_answer = (
                    "I couldn't finish that answer just now. "
                    "Try me again in a moment? ^^"
                )

                st.session_state.tutor_history.append(
                    {
                        "role": "assistant",
                        "content": error_answer,
                    }
                )

                if "typing_placeholder" in locals():
                    typing_placeholder.markdown(
                        tr(error_answer)
                    )

                with ui.expander(
                    "Technical details"
                ):
                    st.code(str(exc))

            else:

                answer = tutor_result["answer"]

                st.session_state.tutor_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                if "typing_placeholder" in locals():
                    typing_placeholder.markdown(
                        answer
                    )

            st.session_state.tutor_history = (
                st.session_state.tutor_history[-20:]
            )

        ui.markdown("---")

        note_col, action_col = st.columns(
            [4.5, 1.5],
            vertical_alignment="center",
        )

        with note_col:
            ui.caption(
                "Found something wrong with the tutor?"
            )

        with action_col:
            if ui.button(
                "let us know",
                key="open_tutor_feedback",
                type="tertiary",
                use_container_width=False,
            ):
                show_tutor_contact()



