import sys
import collections

from tf.convert.recorder import Recorder


combiV = None
combiFreqList = None

padFeatures = set("""
    pdp
    png
    vs
    vt
    typ
    function
    rela
""".strip().split())


def combiFeatures(A):
    api = A.api
    F = api.F

    global combiV
    global combiFreqList

    combiV = {}
    combiFreqList = {}

    def orNull(x):
        return "" if x is None or x == "none" or x == "NA" or x == "unknown" else x

    def pers(x):
        logical = orNull(x)
        return "" if logical == "" else logical[-1]

    def numb(x):
        logical = orNull(x)
        return "" if logical == "" else logical[0]

    png = {}
    pngFreq = collections.Counter()

    for w in F.otype.s("word"):
        combi = (
            f"{pers(F.ps.v(w))}{numb(F.nu.v(w))}{orNull(F.gn.v(w))}{orNull(F.st.v(w))}"
        )
        if combi:
            png[w] = combi
            pngFreq[combi] += 1

    combiV["png"] = png
    combiFreqList["png"] = pngFreq.items()


def makeLegends(maker):
    A = maker.A
    if not combiV:
        combiFeatures(A)

    api = A.api
    Fs = api.Fs

    C = maker.C
    layerSettings = C.layerSettings

    for (level, layer) in (
        ("word", "pdp"),
        ("word", "png"),
        ("word", "vs"),
        ("word", "vt"),
        ("phrase", "function"),
        ("phrase", "ptype"),
        ("clause", "rela"),
        ("clause", "ctype"),
        ("clause", "ttype"),
    ):

        info = layerSettings[level]["layers"][layer]
        feature = info["feature"]

        freqList = (
            combiFreqList["png"]
            if feature == "png"
            else Fs(feature).freqList(nodeTypes={level})
        )
        info["legend"] = sorted(freqList)


def record(maker):
    A = maker.A
    if not combiV:
        combiFeatures(A)

    api = A.api
    F = api.F
    Fs = api.Fs
    L = api.L

    C = maker.C
    layerSettings = C.layerSettings

    clientConfig = maker.clientConfig
    typesLower = clientConfig["typesLower"]
    lingLower = dict(
        sentence=["sentence", "clause", "phrase"],
        clause=["clause", "phrase"],
        phrase=["phrase"],
    )
    lingBoundary = {
        False: {
            True: dict(
                sentence="┣",
                clause="┏",
                phrase="◀",
            ),
            False: dict(
                sentence="┫\n",
                clause="┓",
                phrase="▶",
            ),
        },
        True: {
            True: dict(
                sentence="├",
                clause="┌",
                phrase="◁",
            ),
            False: dict(
                sentence="┤",
                clause="┐",
                phrase="▷",
            ),
        },
    }

    A.indent(reset=True)
    A.info("preparing ... ")

    A.info("start recording")

    up = {}
    recorders = {}
    accumulators = {}
    maker.up = up
    maker.recorders = recorders
    maker.accumulators = accumulators

    for (level, typeInfo) in layerSettings.items():
        ti = typeInfo.get("layers", None)
        if ti is None:
            continue

        recorders[level] = {
            layer: Recorder(api) for layer in ti if ti[layer]["pos"] is None
        }
        accumulators[level] = {layer: [] for layer in ti if ti[layer]["pos"] is not None}

    def addValue(node, use=None):
        returnValue = None

        level = use or F.otype.v(node)
        typeInfo = layerSettings[level]
        theseLayers = typeInfo.get("layers", {})

        first = True

        for layer in theseLayers:
            info = theseLayers[layer]
            descend = info.get("descend", False)
            ascend = info.get("ascend", False)
            feature = info.get("feature", None)
            afterFeature = info.get("afterFeature", None)
            afterDefault = info.get("afterDefault", None)
            vMap = info.get("legend", None)
            if type(vMap) is not dict:
                vMap = None
            default = info["default"]
            pos = info["pos"]

            png = combiV["png"]

            featureFunc = (
                (lambda n: png.get(n, None))
                if feature == "png"
                else Fs(feature).v
            )

            if descend:
                value = ""
                for n in L.d(node, otype=descend):
                    val = featureFunc(n)
                    if vMap:
                        val = vMap.get(val, default)
                    else:
                        val = val or default

                    value += str(val)
            else:
                refNode = L.u(node, otype=ascend)[0] if ascend else node
                value = featureFunc(refNode)
                if vMap:
                    value = vMap.get(value, default)
                else:
                    value = value or default

            if feature in padFeatures:
                value = f"{value:<4}"

            afterVal = ""
            if afterFeature is not None:
                afterVal = Fs(afterFeature).v(node)
            if not afterVal and afterDefault:
                afterVal = afterDefault
            value = f"{value}{afterVal}"

            if pos is None:
                recorders[level][layer].add(value)
            else:
                accumulators[level][layer].append(value)

            if first:
                returnValue = value
                first = False

        return returnValue

    def lingStart(level, inner):
        outer = L.u(inner, otype=level)[0]
        outerFirst = L.d(outer, otype="word")[0]
        innerFirst = L.d(inner, otype="word")[0]
        addLing(level, innerFirst != outerFirst, True)

    def lingEnd(level, inner):
        outer = L.u(inner, otype=level)[0]
        outerLast = L.d(outer, otype="word")[-1]
        innerLast = L.d(inner, otype="word")[-1]
        addLing(level, innerLast != outerLast, False)

    def addLing(level, isAtom, isStart):
        value = lingBoundary[isAtom][isStart][level]
        for lType in lingLower.get(level):
            if lType in recorders:
                for (lr, x) in recorders[lType].items():
                    x.add(value)
            if lType in accumulators:
                for x in accumulators[lType].values():
                    x.append(value)

    def addAfterValue(node):
        level = F.otype.v(node)
        typeInfo = layerSettings[level]
        value = typeInfo.get("afterDefault", None)
        if value:
            addLevel(level, value)

    def addAfterWord(node):
        if F.trailer.v(node).startswith("00"):
            addLevel("word", "\n")

    def addAll(level, value):
        lowerTypes = typesLower[level]
        for lType in lowerTypes:
            if lType in recorders:
                for x in recorders[lType].values():
                    x.add(value)
            if lType in accumulators:
                for x in accumulators[lType].values():
                    x.append(value)

    def addLevel(level, value):
        if level in recorders:
            for x in recorders[level].values():
                x.add(value)
        if level in accumulators:
            for x in accumulators[level].values():
                x.append(value)

    def addLayer(level, layer, value):
        if level in recorders:
            if layer in recorders[level]:
                recorders[level][layer].add(value)
        if level in accumulators:
            if layer in accumulators[level]:
                accumulators[level][layer].append(value)

    def startNode(node, asType=None):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders

        level = asType or F.otype.v(node)

        if level in recorders:
            for rec in recorders[level].values():
                rec.start(node)

    def endNode(node, asType=None):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders
        level = asType or F.otype.v(node)

        if level in recorders:
            for rec in recorders[level].values():
                rec.end(node)

    # note the `up[n] = m` statements below:
    # we only let `up` connect nodes from one level to one level higher

    for (i, book) in enumerate(F.otype.s("book")):
        startNode(book)
        title = addValue(book)
        sys.stdout.write("\r" + f"{i + 1:>3} {title:<80}")

        for chapter in L.d(book, otype="chapter"):
            up[chapter] = book
            startNode(chapter)
            addValue(chapter)

            verses = L.d(chapter, otype="verse")
            verse = verses[0]
            lastVerse = verses[-1]
            endVerse = L.d(verse, otype="word")[-1]
            up[verse] = chapter
            startNode(verse)
            addValue(verse)

            for sentence in L.d(chapter, otype="sentence_atom"):
                up[sentence] = verse
                startNode(sentence, asType="sentence")
                lingStart("sentence", sentence)
                addValue(sentence, use="sentence")

                for clause in L.d(sentence, otype="clause_atom"):
                    up[clause] = sentence
                    startNode(clause, asType="clause")
                    lingStart("clause", clause)
                    addValue(clause, use="clause")

                    for phrase in L.d(clause, otype="phrase_atom"):
                        up[phrase] = clause
                        startNode(phrase, asType="phrase")
                        lingStart("phrase", phrase)
                        addValue(phrase, use="phrase")

                        for word in L.d(phrase, otype="word"):
                            up[word] = phrase
                            startNode(word)
                            addValue(word)
                            addAfterWord(word)
                            endNode(word)
                            if word == endVerse:
                                addAfterValue(verse)
                                endNode(verse)
                                if verse != lastVerse:
                                    verse = L.n(verse, otype="verse")[0]
                                    up[verse] = chapter
                                    endVerse = L.d(verse, otype="word")[-1]
                                    startNode(verse)
                                    addValue(verse)

                        lingEnd("phrase", phrase)
                        endNode(phrase, asType="phrase")
                    lingEnd("clause", clause)
                    endNode(clause, asType="clause")
                lingEnd("sentence", sentence)
                endNode(sentence, asType="sentence")
            addAfterValue(chapter)
            endNode(chapter)
        addAfterValue(book)
        endNode(book)

    sys.stdout.write("\n")
    A.info("done")
