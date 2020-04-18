from tf.core.helpers import htmlEsc
from tf.applib.helpers import dh
from tf.applib.api import setupApi
from tf.applib.links import outLink

SHEBANQ_URL = "https://shebanq.ancient-data.org/hebrew"

SHEBANQ = (
    f"{SHEBANQ_URL}/text"
    "?book={book}&chapter={chapter}&verse={verse}&version={version}"
    "&mr=m&qw=q&tp=txt_p&tr=hb&wget=v&qget=v&nget=vt"
)

SHEBANQ_LEX = f"{SHEBANQ_URL}/word" "?version={version}&id={lid}"


def notice(app):
    if int(app.api.TF.version.split(".")[0]) <= 7:
        print(
            f"""
Your Text-Fabric is outdated.
It cannot load this version of the TF app `{app.appName}`.
Recommendation: upgrade Text-Fabric to version 8.
Hint:

    pip3 install --upgrade text-fabric

"""
        )


class TfApp(object):
    def __init__(*args, **kwargs):
        setupApi(*args, **kwargs)
        notice(args[0])

    def webLink(app, n, text=None, className=None, _asString=False, _noUrl=False):
        api = app.api
        T = api.T
        F = api.F
        version = app.version
        nType = F.otype.v(n)
        if nType == "lex":
            lex = F.lex.v(n)
            lan = F.language.v(n)
            lexId = "{}{}".format(
                "1" if lan == "Hebrew" else "2",
                lex.replace(">", "A")
                .replace("<", "O")
                .replace("[", "v")
                .replace("/", "n")
                .replace("=", "i"),
            )
            href = SHEBANQ_LEX.format(version=version, lid=lexId)
            title = "show this lexeme in SHEBANQ"
            if text is None:
                text = htmlEsc(F.voc_lex_utf8.v(n))
            result = outLink(text, href, title=title, className=className)
            if _asString:
                return result
            dh(result)
            return

        (bookLa, chapter, verse) = T.sectionFromNode(n, lang="la", fillup=True)
        passageText = app.sectionStrFromNode(n)
        href = (
            "#"
            if _noUrl
            else SHEBANQ.format(
                version=version, book=bookLa, chapter=chapter, verse=verse,
            )
        )
        if text is None:
            text = passageText
            title = "show this passage in SHEBANQ"
        else:
            title = passageText
        if _noUrl:
            title = None
        target = "" if _noUrl else None
        result = outLink(
            text,
            href,
            title=title,
            className=className,
            target=target,
            passage=passageText,
        )
        if _asString:
            return result
        dh(result)
