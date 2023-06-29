
document.getElementById("ask").addEventListener("click", () => {
    const divPergunta = document.createElement("div");
    divPergunta.className = "divPergunta";
    divPergunta.innerText = "Q: " +document.getElementById("questionbox").value;
    document.getElementById("respostas").append(divPergunta);
    browser.runtime.sendMessage({
        command: "question",
        question: document.getElementById("questionbox").value,
        items: document.getElementById("items").value
    });
    document.getElementById("ask").disabled = true;
})

browser.runtime.onMessage.addListener((message) => {
    console.log("got message in sidebar", message);
    if (message.command === "indexing") {
        console.log("na sidebar = display indexing na ui");
        document.getElementById("status").innerText = "Indexing...";
        document.getElementById("status").style.display = "block";
    } else if (message.command === "indexed") {
        console.log("na sidebar = remove indexing na ui");
        document.getElementById("status").innerText = "";
    }
    else if (message.command === "processing") {
        console.log("na sidebar = add processing msg");
        document.getElementById("status").innerText = "Processing...";
        document.getElementById("status").style.display = "block";
    }
    else if (message.command === "processed") {
        console.log("na sidebar = add processing msg");
        document.getElementById("status").innerText = "";
        const divResposta = document.createElement("div");
        divResposta.className = "divResposta";
        const confidenceFilter = document.getElementById("confidenceFilter").value;
        for (let response in message.responses) {
            if (document.getElementById("filterByconfidence").checked &&
                (message.responses[response].hitscore < confidenceFilter || message.responses[response].answer.score < confidenceFilter)) {
                    const confidence = document.createElement("a");
                    confidence.innerText = "This response was filter due low confidence.";
                    confidence.className = "respostaLink";
                    confidence.title = message.responses[response].hitscore  + "," + message.responses[response].answer.score;
                    divResposta.append(document.createElement("br"));
                    divResposta.append(confidence);
            } else {
                const answer = document.createElement("a");
                answer.href = message.responses[response].hitpayload.url;
                answer.innerText = String.fromCodePoint(0x1F64B) + " " + message.responses[response].answer.answer.replace(/(\r\n|\n|\r)/gm, "");
                answer.className = "respostaLink";

                const href = document.createElement("a");
                href.href = message.responses[response].hitpayload.url;
                href.innerText = String.fromCodePoint(0x1F517) + " " + message.responses[response].hitpayload.title;
                href.className = "respostaLink";

                divResposta.append(answer);
                divResposta.append(document.createElement("br"));
                divResposta.append(href);
                if ((message.responses[response].hitscore < confidenceFilter || message.responses[response].answer.score < confidenceFilter)) {
                    const confidence = document.createElement("a");
                    confidence.innerText = "Low confidence";
                    confidence.className = "confidence";
                    confidence.title = message.responses[response].hitscore  + "," + message.responses[response].answer.score;
                    divResposta.append(document.createElement("br"));
                    divResposta.append(confidence);
                }
            }
            document.getElementById("respostas").append(divResposta);
            divResposta.append(document.createElement("hr"));
        }
        document.getElementById("ask").disabled = false;
    }
});


