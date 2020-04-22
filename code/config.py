from os.path import dirname, abspath

API_VERSION = 1

PROTOCOL = "http://"
HOST = "localhost"
PORT = dict(kernel=18981, web=8101)

ORG = "etcbc"
REPO = "bhsa"
CORPUS = "BHSA = Biblia Hebraica Stuttgartensia Amstelodamensis"
VERSION = "c"
RELATIVE = "tf"

DOI_TEXT = "10.5281/zenodo.1007624"
DOI_URL = "https://doi.org/10.5281/zenodo.1007624"

DOC_URL = f"https://{ORG}.github.io/{REPO}"
DOC_INTRO = "0_home"
CHAR_URL = "{tfDoc}/Writing/Hebrew"
CHAR_TEXT = ("Hebrew characters and transcriptions")

FEATURE_URL = f"{DOC_URL}/features/{{feature}}"

MODULE_SPECS = (
    dict(
        org=ORG,
        repo="phono",
        relative=RELATIVE,
        corpus="Phonetic Transcriptions",
        docUrl=(
            "https://nbviewer.jupyter.org/github/etcbc/phono"
            "/blob/master/programs/phono.ipynb"
        ),
        doiText="10.5281/zenodo.1007636",
        doiUrl="https://doi.org/10.5281/zenodo.1007636",
    ),
    dict(
        org=ORG,
        repo="parallels",
        relative=RELATIVE,
        corpus="Parallel Passages",
        docUrl=(
            "https://nbviewer.jupyter.org/github/etcbc/parallels"
            "/blob/master/programs/parallels.ipynb"
        ),
        doiText="10.5281/zenodo.1007642",
        doiUrl="https://doi.org/10.5281/zenodo.1007642",
    ),
)
ZIP = [REPO] + [m["repo"] for m in MODULE_SPECS]

STANDARD_FEATURES = """
    pdp vs vt
    lex language gloss
    voc_lex voc_lex_utf8
    function typ rela number
    label
"""

if VERSION in {"4", "4b"}:
    STANDARD_FEATURES.replace("voc_", "g_")
STANDARD_FEATURES = STANDARD_FEATURES.strip().split()

EXCLUDED_FEATURES = set(
    """
    crossrefLCS
    crossrefSET
    dist
    dist_unit
    distributional_parent
    freq_occ
    functional_parent
    g_nme
    g_nme_utf8
    g_pfm
    g_pfm_utf8
    g_prs
    g_prs_utf8
    g_uvf
    g_uvf_utf8
    g_vbe
    g_vbe_utf8
    g_vbs
    g_vbs_utf8
    instruction
    is_root
    kind
    kq_hybrid
    kq_hybrid_utf8
    languageISO
    lex0
    lexeme_count
    mother_object_type
    rank_occ
    root
    suffix_gender
    suffix_number
    suffix_person
""".strip().split())

EXAMPLE_SECTION = (
    f"<code>Genesis 1:1</code> (use"
    f' <a href="https://github.com/{ORG}/{REPO}'
    f'/blob/master/tf/{VERSION}/book%40en.tf" target="_blank">'
    f"English book names</a>)"
)
EXAMPLE_SECTION_TEXT = "Genesis 1:1"

DATA_DISPLAY = dict(
    noneValues={None, "NA", "none", "unknown"},
    sectionSep1=" ",
    sectionSep2=":",
    writing="hbo",
    writingDir="rtl",
    fontName="Ezra SIL",
    font="SILEOT.ttf",
    fontw="SILEOT.woff",
    textFormats={},
    browseNavLevel=2,
    browseContentPretty=False,
)

TYPE_DISPLAY = dict(
    book=dict(
        template="{book}",
        children="chapter",
        level=3, flow="col", wrap=False, stretch=False,
    ),
    chapter=dict(
        template="{chapter}",
        children="verse",
        level=3, flow="col", wrap=False, strectch=False,
    ),
    verse=dict(
        template="{verse}",
        children="sentence_atom",
        condense=True,
        level=3, flow="col", wrap=False, strectch=False,
    ),
    half_verse=dict(
        template="{label}",
        children="sentence_atom",
        verselike=True,
        level=3, flow="col", wrap=False, strectch=False,
    ),
    sentence=dict(
        template="",
        featuresBare="number",
        children="sentence_atom",
        level=3, flow="row", wrap=True, strectch=True,
    ),
    sentence_atom=dict(
        template="",
        featuresBare="number",
        children="clause_atom",
        super="sentence",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    clause=dict(
        template="",
        featuresBare="rela",
        features="typ",
        children="clause_atom",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    clause_atom=dict(
        template="",
        featuresBare="code",
        children="phrase_atom",
        super="clause",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    phrase=dict(
        template="",
        featuresBare="function",
        features="typ",
        children="phrase_atom",
        level=2, flow="row", wrap=True, strectch=True,
    ),
    phrase_atom=dict(
        template="",
        featuresBare="rela",
        features="typ",
        children="word",
        super="phrase",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    subphrase=dict(
        template="",
        featuresBare="number",
        children="word",
        level=1, flow="row", wrap=True, strectch=True,
    ),
    lex=dict(
        template="{voc_lex_utf8",
        featuresBare="gloss",
        lexTarget="word",
        level=0, flow="col", wrap=False, strectch=False,
    ),
    word=dict(
        template=True,
        featuresBare="lex:gloss",
        features="pdp vs vt",
        base=True,
        level=0, flow="col", wrap=False, strectch=False,
    ),
)

INTERFACE_DEFAULTS = dict()


def deliver():
    return (globals(), dirname(abspath(__file__)))
