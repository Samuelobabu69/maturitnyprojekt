target = "127.0.0.1"

async function request (method, type, data) {

    let message = JSON.stringify({type: type, data: data});

    let response = await fetch(`http://${target}:80`, {
        method: method,
        headers: {
            "Content-Type": "application/json",
            "Content-Length": message.length

        },
        body: message
    });

    return response;
}

post("type123", "data123");

console.log("JS received!");