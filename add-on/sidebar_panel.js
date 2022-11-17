document.getElementById("ask").addEventListener("click", () => {
    document.getElementById("respostas").append(document.createElement("hr"));

    browser.runtime.sendMessage({
        type: "question",
        payload: document.getElementById("questionbox").value
    });
})

browser.runtime.onMessage.addListener((message) => {
    console.log("got message in sidebar", JSON.stringify(message));
    const divResposta = document.createElement("li");
    divResposta.innerText = message.payload;
    document.getElementById("respostas").append(divResposta);
    document.getElementById("respostas").append(document.createElement("br"));

});


