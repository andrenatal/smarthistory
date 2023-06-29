/*
On startup, connect to the "ping_pong" app.
*/
var port = browser.runtime.connectNative("smarthistory");

/*
Listen for messages from the app.
*/
port.onMessage.addListener((response) => {
  console.log("got message in bgsript from native", response);
  response = JSON.parse(response);
  browser.runtime.sendMessage(response);
});

browser.runtime.onMessage.addListener(async (message, sender) => {
  console.log("got message in bgsript", message);
  switch (message.command) {
    case "monitorTabLoad": {
      browser.tabs.executeScript(
        sender.tab.id,
        {code: 'document.documentElement.innerHTML'},
        (results) =>{
            port.postMessage({
              command: "index",
              url: sender.tab.url,
              title: sender.tab.title,
              body: results[0]
            });
        }
      );
      break;
    }
    case "question": {
      // envia mensagem para o nativemsg
      port.postMessage({
        command: "question",
        question: message.question,
        items: message.items
      });
    }
  }
});