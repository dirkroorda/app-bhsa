import sys

from tf.convert.recorder import Recorder


def makeLegends(maker):
    pass


def record(maker):
    A = maker.A
    api = A.api
    F = api.F
    Fs = api.Fs
    L = api.L

    C = maker.C
    layerSettings = C.layerSettings

    clientConfig = maker.clientConfig
    typesLower = clientConfig["typesLower"]

    A.indent(reset=True)
    A.info("preparing ... ")

    def orNull(x):
        return "" if x is None or x == "none" or x == "NA" or x == "unknown" else x

    def pers(x):
        logical = orNull(x)
        return "" if logical == "" else logical[-1]

    def numb(x):
        logical = orNull(x)
        return "" if logical == "" else logical[0]

    png = {}

    for w in F.otype.s("word"):
        combi = (
            f"{pers(F.ps.v(w))}{numb(F.nu.v(w))}{orNull(F.gn.v(w))}{orNull(F.st.v(w))}"
        )
        if combi:
            png[w] = combi

    vb = {}

    for w in F.otype.s("word"):
        combi = f"{orNull(F.vs.v(w))}-{orNull(F.vt.v(w))}"
        if combi and combi != "-":
            vb[w] = combi

    A.info("start recording")

    up = {}
    texts = {}
    positions = {}
    recorders = {}
    accumulators = {}

    for (nType, typeInfo) in layerSettings.items():
        ti = typeInfo.get("layers", None)
        if ti is None:
            continue

        texts[nType] = {name: None for name in ti}
        positions[nType] = {name: None for name in ti if ti[name]["pos"] is None}
        recorders[nType] = {
            name: Recorder(api) for name in ti if ti[name]["pos"] is None
        }
        accumulators[nType] = {name: [] for name in ti if ti[name]["pos"] is not None}

    def addValue(node):
        returnValue = None

        nType = F.otype.v(node)
        typeInfo = layerSettings[nType]
        theseLayers = typeInfo.get("layers", {})

        first = True

        for name in theseLayers:
            info = theseLayers[name]
            descend = info.get("descend", False)
            ascend = info.get("ascend", False)
            feature = info.get("feature", None)
            preFeature = info.get("preFeature", None)
            preDefault = info.get("preDefault", None)
            preFixed = info.get("preFixed", None)
            afterFeature = info.get("afterFeature", None)
            afterDefault = info.get("afterDefault", None)
            afterFixed = info.get("afterFixed", None)
            vMap = info.get("legend", None)
            default = info["default"]
            pos = info["pos"]

            featureFunc = (
                (lambda n: png.get(n, None))
                if feature == "png"
                else (lambda n: vb.get(n, None))
                if feature == "vb"
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

            preVal = ""
            if preFeature is not None:
                preVal = Fs(preFeature).v(node)
                if not preVal and preDefault:
                    preVal = preDefault
            if preFixed is not None:
                preVal = f"{preFixed}{preVal}"

            afterVal = ""
            if afterFeature is not None:
                afterVal = Fs(afterFeature).v(node)
                if not afterVal and afterDefault:
                    afterVal = afterDefault
            if afterFixed is not None:
                afterVal = f"{afterVal}{afterFixed}"
            value = f"{preVal}{value}{afterVal}"

            if pos is None:
                recorders[nType][name].add(value)
            else:
                accumulators[nType][name].append(value)

            if first:
                returnValue = value
                first = False

        return returnValue

    def outerStart(nType, inner):
        outer = L.u(inner, otype=nType)[0]
        outerFirst = L.d(outer, otype="word")[0]
        innerFirst = L.d(inner, otype="word")[0]
        if innerFirst == outerFirst:
            addHere(f"{nType}_atom", "{")

    def outerEnd(nType, inner, nl=False):
        outer = L.u(inner, otype=nType)[0]
        outerLast = L.d(outer, otype="word")[-1]
        innerLast = L.d(inner, otype="word")[-1]
        if innerLast == outerLast:
            addHere(f"{nType}_atom", "}")
            if nl:
                addAll(f"{nType}_atom", "\n")

    def addPreValue(node):
        nType = F.otype.v(node)
        typeInfo = layerSettings[nType]
        preFeature = typeInfo.get("preFeature", None)
        preDefault = typeInfo.get("preDefault", None)
        preFixed = typeInfo.get("preFixed", None)
        value = ""
        if preFeature is not None:
            value = Fs(preFeature).v(node)
        if preDefault is not None:
            if not value:
                value = preDefault
            if value:
                addAll(nType, value)
        if preFixed:
            addHere(nType, preFixed)

    def addAfterValue(node):
        nType = F.otype.v(node)
        typeInfo = layerSettings[nType]
        afterFeature = typeInfo.get("afterFeature", None)
        afterDefault = typeInfo.get("afterDefault", None)
        afterFixed = typeInfo.get("afterFixed", None)
        if afterFixed:
            addHere(nType, afterFixed)
        value = ""
        if afterFeature is not None:
            value = Fs(afterFeature).v(node)
        if afterDefault is not None:
            if not value:
                value = afterDefault
            if value:
                addAll(nType, value)

    def addAll(nType, value):
        lowerTypes = typesLower[nType]
        for nt in lowerTypes:
            if nt in recorders:
                for x in recorders[nt].values():
                    x.add(value)
            if nt in accumulators:
                for x in accumulators[nt].values():
                    x.append(value)

    def addHere(nType, value):
        if nType in recorders:
            for x in recorders[nType].values():
                x.add(value)
        if nType in accumulators:
            for x in accumulators[nType].values():
                x.append(value)

    def deliverAll():
        for (nType, typeInfo) in recorders.items():
            for (name, x) in typeInfo.items():
                texts[nType][name] = x.text()
                # here we are going to use that there is at most one node per node type
                # that corresponds to a character position
                positions[nType][name] = [
                    tuple(nodes)[0] if nodes else None for nodes in x.positions()
                ]

        for (nType, typeInfo) in accumulators.items():
            for (name, x) in typeInfo.items():
                texts[nType][name] = "".join(x)

    def startNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders

        nType = F.otype.v(node)

        if nType in recorders:
            for rec in recorders[nType].values():
                rec.start(node)

    def endNode(node):
        # we have organized recorders by node type
        # we only record nodes of matching type in recorders
        nType = F.otype.v(node)

        if nType in recorders:
            for rec in recorders[nType].values():
                rec.end(node)

    # note the `up[n] = m` statements below:
    # we only let `up` connect nodes from one level to one level higher

    for (i, book) in enumerate(F.otype.s("book")):
        startNode(book)
        name = addValue(book)
        sys.stdout.write("\r" + f"{i + 1:>3} {name:<80}")

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
                startNode(sentence)
                outerStart("sentence", sentence)
                addPreValue(sentence)
                addValue(sentence)

                for clause in L.d(sentence, otype="clause_atom"):
                    up[clause] = sentence
                    startNode(clause)
                    outerStart("clause", clause)
                    addPreValue(clause)
                    addValue(clause)

                    for phrase in L.d(clause, otype="phrase_atom"):
                        up[phrase] = clause
                        startNode(phrase)
                        outerStart("phrase", phrase)
                        addPreValue(phrase)
                        addValue(phrase)

                        for word in L.d(phrase, otype="word"):
                            up[word] = phrase
                            startNode(word)
                            addValue(word)
                            addAfterValue(word)
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

                        addAfterValue(phrase)
                        outerEnd("phrase", phrase)
                        endNode(phrase)
                    addAfterValue(clause)
                    outerEnd("clause", clause, nl=True)
                    endNode(clause)
                addAfterValue(sentence)
                outerEnd("sentence", sentence)
                endNode(sentence)
            addAfterValue(chapter)
            endNode(chapter)
        addAfterValue(book)
        endNode(book)

    deliverAll()

    sys.stdout.write("\n")

    data = dict(
        texts=texts,
        positions=positions,
        up=maker.compress(up),
    )
    maker.data = data
    sys.stdout.write("\n")
    A.info("done")
