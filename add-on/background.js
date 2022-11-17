/*
On startup, connect to the "ping_pong" app.
*/
var port = browser.runtime.connectNative("drqa");

/*
Listen for messages from the app.
*/
port.onMessage.addListener((response) => {
  console.log("got message in bgsript from native", response);

  browser.runtime.sendMessage({
    type: "answer",
    payload: response
  });
});

/*
On a click on the browser action, send the app a message.
*/
browser.browserAction.onClicked.addListener(() => {
  console.log("Sending:  ping");
  //
});

browser.runtime.onMessage.addListener((message) => {
  console.log("got message in bgsript", JSON.stringify(message));
  port.postMessage(message.payload);
});

