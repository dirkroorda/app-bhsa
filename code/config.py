from os.path import dirname, abspath

API_VERSION = 1

PROVENANCE_SPEC = dict(
    org="etcbc",
    repo="bhsa",
    version="c",
    moduleSpecs=(
        dict(
            repo="phono",
            org="etcbc",
            doi="10.5281/zenodo.1007636",
            corpus="Phonetic Transcriptions",
            docUrl="{nbUrl}/etcbc/phono/blob/master/programs/phono.ipynb",
        ),
        dict(
            repo="parallels",
            doi="10.5281/zenodo.1007642",
            corpus="Parallel Passages",
            docUrl="{nbUrl}/{org}/parallels/blob/master/programs/parallels.ipynb",
        ),
    ),
    doi="10.5281/zenodo.1007624",
    corpus="BHSA = Biblia Hebraica Stuttgartensia Amstelodamensis",
    webBase="https://shebanq.ancient-data.org/hebrew",
    webUrl=(
        "{base}/text"
        "?book=<1>&chapter=<2>&verse=<3>&version={version}"
        "&mr=m&qw=q&tp=txt_p&tr=hb&wget=v&qget=v&nget=vt"
    ),
    webUrlLex="{base}/word?version={version}&id={lid}",
    webLang="la",
    webHint="Show this on SHEBANQ",
)

DOCS = dict(
    docExt="",
    docRoot="https://{org}.github.io",
    docBase="{docRoot}/{repo}",
    docPage="0_home",
    featurePage="0_home",
)

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
""".strip().split()
)


DATA_DISPLAY = dict(
    noneValues={None, "NA", "none", "unknown"},
    excludedFeatures=EXCLUDED_FEATURES,
    writing="hbo",
    exampleSectionHtml=(
        "<code>Genesis 1:1</code> (use"
        ' <a href="https://github.com/{org}/{repo}'
        '/blob/master/tf/{version}/book%40en.tf" target="_blank">'
        "English book names</a>)"
    ),
)

TYPE_DISPLAY = dict(
    verse=dict(children="sentence_atom"),
    half_verse=dict(template="{label}", children="sentence_atom", verselike=True),
    sentence=dict(featuresBare="number", children="sentence_atom"),
    sentence_atom=dict(
        featuresBare="number", children="clause_atom", super="sentence", level=1,
    ),
    clause=dict(featuresBare="rela", features="typ", children="clause_atom"),
    clause_atom=dict(
        featuresBare="code", children="phrase_atom", super="clause", level=1,
    ),
    phrase=dict(featuresBare="function", features="typ", children="phrase_atom"),
    phrase_atom=dict(
        featuresBare="rela", features="typ", children="word", super="phrase", level=1,
    ),
    subphrase=dict(featuresBare="number", children="word"),
    lex=dict(template="{voc_lex_utf8}", featuresBare="gloss", lexOcc="word"),
    word=dict(featuresBare="lex:gloss", features="pdp vs vt"),
)

INTERFACE_DEFAULTS = dict()


def deliver():
    return (globals(), dirname(abspath(__file__)))
