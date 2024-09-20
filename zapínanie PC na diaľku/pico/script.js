$(document).ready(() => {
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

    function inactiveLogout () {

        // A timer that forces the client to disconnect after 60s of inactivity

        clearTimeout(logoutTime);
        logoutTime = setTimeout(() => {
            post("empty", "inactive dc")
            connectScreen.css("display", "flex")
            main.css("display", "none")
            $(document).off("touchstart");
            $(document).off("touchmove");
            $(document).off("touchend");
            connectError.text("Disconnected for inactivity.")
            clearInterval(updateScreen);
            menuState = 0;
            menu.css("left", "-100vw");
        }, 60000);
    }

    function connected () {

        // Shows the connect screen and initiates the timer for inactive logout

        connectScreen.css("display", "none");
        main.css("display", "flex");

        inactiveLogout();
        $(document).on("touchstart", () => {
            inactiveLogout();
        })
        $(document).on("touchmove", () => {
            inactiveLogout();
        })
        $(document).on("touchend", () => {
            inactiveLogout();
        })
    }

    function adminConnected () {
        adminSettingsAccessButton.css("display", "none");
        adminSettingsPasswordInput.css("display", "none");
        adminSettingsError.css("display", "none");
        adminSettingsLoading.css("display", "none");
    }

    function adminSettingsShowButtonClick () {

        if (adminSettingsScreen.css("right") != "0px") {
            adminSettingsScreen.css("right", 0)
            adminSettingsShowButton.css("transform", "rotate(180deg)");
        } else {
            adminSettingsScreen.css("right", "-100vw")
            adminSettingsShowButton.css("transform", "rotate(0deg)");
        }

    }

    async function adminSettingsAccessButtonClick () {

        adminSettingsAccessButton.prop("disabled", true);
        adminSettingsAccessButton.css("opacity", 0.5);
        adminSettingsLoading.css("opacity", 1);
        adminSettingsError.text("");

        let password = adminSettingsPasswordInput.val().trim();
        let response;

        let ttl = new Promise((_, reject) => {
            setTimeout(() => reject("ttlReached"), 7000);
        })

        try {
            response = await Promise.race([request("POST", "accessAttempt", password), ttl]);
        } catch (error) {
            response = error;
        }

        console.log(response);

        if (response.status === 200) {
            adminConnected();

        } else if (response.status === 401) {
            adminSettingsError.text("Incorrect password");

        } else if (response === "ttlReached") {
            adminSettingsError.text("Target device refused connection");

        } else {
            adminSettingsError.text("Unknown error");
        }

        adminSettingsAccessButton.prop("disabled", false);
        adminSettingsAccessButton.css("opacity", 1);
        adminSettingsLoading.css("opacity", 0);
    }

    async function connectButtonClick () {

        // After pressing the connect button, sends a request with a password.
        // Also handles any errors returned from server

        connectButton.prop("disabled", true);
        connectButton.css("opacity", 0.5);
        connectLoading.css("opacity", 1);
        connectError.text("");

        let password = connectPasswordInput.val().trim();
        let response;

        let ttl = new Promise((_, reject) => {
            setTimeout(() => reject("ttlReached"), 7000);
        })

        try {
            response = await Promise.race([request("POST", "accessAttempt", password), ttl]);
        } catch (error) {
            response = error;

        }

        console.log(response);

        if (response.status === 200) {
            connected();

        } else if (response.status === 401) {
            connectError.text("Incorrect password");

        } else if (response.status === 409) {
            connectError.text("Target device is occupied");

        } else if (response === "ttlReached") {
            connectError.text("Target device refused connection");

        } else {
            connectError.text("Unknown error");

        }

        connectButton.prop("disabled", false);
        connectButton.css("opacity", 1);
        connectLoading.css("opacity", 0);
    }

    let target_w_port = new URL(window.location.href).origin.substring(7);
    let target = target_w_port.substring(0, target_w_port.length + 2)
        
    const connectScreen = $(".connect-screen");
    const main = $(".main");
    const powerButton = $(".power-button");
    const connectPasswordInput = $("#connect-password");
    const connectButton = $(".connect-button");
    const connectLoading = $(".connect-loading");
    const connectError = $(".connect-error");
    const adminSettingsPasswordInput = $("#admin-settings-password");
    const adminSettingsShowButton = $(".admin-settings-show-button");
    const adminSettingsAccessButton = $(".admin-settings-access-button")
    const adminSettingsLoading = $(".admin-settings-loading");
    const adminSettingsError = $(".admin-settings-error");
    const adminSettingsScreen = $(".admin-settings-screen");

    connectButton.click(connectButtonClick);
    adminSettingsShowButton.click(adminSettingsShowButtonClick);
    adminSettingsAccessButton.click(adminSettingsAccessButtonClick);

    $(powerButton).on("touchstart", (event) => {
        request("POST", "powerButton", "press");
    });

    $(powerButton).on("touchend", (event) => {
        request("POST", "powerButton", "release");
    });
});
