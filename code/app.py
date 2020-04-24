from tf.applib.api import setupApi


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
    def __init__(app, *args, **kwargs):
        setupApi(app, *args, **kwargs)
        notice(app)

    def getLexId(app, n):
        api = app.api
        F = api.F

        lex = F.lex.v(n)
        lan = F.language.v(n)
        return "{}{}".format(
            "1" if lan == "Hebrew" else "2",
            lex.replace(">", "A")
            .replace("<", "O")
            .replace("[", "v")
            .replace("/", "n")
            .replace("=", "i"),
        )
