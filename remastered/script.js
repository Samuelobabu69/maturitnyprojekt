$(document).ready(() => {

    const showPasswordBtn = $(".show-password-btn");
    const showPasswordBtnImg = $(".show-password-btn img");
    const accessPasswordInput = $("#access-password");
    

    /// Mousepad ///

    const mousepad = $(".mousepad");
    const keyboard = $(".keyboard");
    const keyboardToMousepadSwitch = $(".keyboard-to-mousepad-switch");
    const mousepadToKeyboardSwitch = $(".mousepad-to-keyboard-switch");
    let keyboardHidden = true;

    mousepadToKeyboardSwitch.on('contextmenu touchstart', function (e) {
        e.preventDefault(); 
    })

    keyboardToMousepadSwitch.on('contextmenu touchstart', function (e) {
        e.preventDefault(); 
    })

    mousepadToKeyboardSwitch.on("touchstart", () => {
        if (keyboardHidden) {
            keyboardHidden = false;
            keyboard.css("bottom", "0");
            mousepadToKeyboardSwitch.css("bottom", "190px");
            keyboardToMousepadSwitch.css("bottom", "265px")
        } 
    });

    keyboardToMousepadSwitch.on("touchstart", () => {
        if (!keyboardHidden) {
            keyboardHidden = true;
            keyboard.css("bottom", "-260px");
            keyboardToMousepadSwitch.css("bottom", "190px");
            mousepadToKeyboardSwitch.css("bottom", "265px")
        } 
    });


    /// Keyboard ///

    const keyboardKeys = $(".key");
    const shiftAffectedKeys = $(".shift-affected-key");
    const aftertapKeys = $(".aftertap-key");

    
    const keyboardLetters = $(".keyboard-letters");
    const keyboardNumbers = $(".keyboard-numbers");
    const keyboardSymbols = $(".keyboard-symbols");
    const LToNKey = $(".l-to-n-key");
    const NToLKey = $(".n-to-l-key");
    const NToSKey = $(".n-to-s-key");
    const SToNKey = $(".s-to-n-key");
    const shiftKey = $(".shift-key");
    const shiftKeyImg = $(".shift-key img");

    // Keys that have alternate keys when you hold them
    let alternateKeys = $.getJSON("keyboard-alternate-keys.json", (data) => {
        alternateKeys = data;
    });
    let shiftState = 0;
    let keyAlternateSelectorIndex = 0;
    let typingAlternate = false;
    let keyToSend;

    function findAlternateKey (key) {
        // Finds alternate key in the alternateKeys array
        for (let index = 0; index < alternateKeys.length; index++) {
            const pair = alternateKeys[index];

            if (pair[0] === key) {
                return pair[1];
            }
        }
        return false;
    }

    // Button to show/hide password on the login page
    showPasswordBtn.click(() => {
        if (accessPasswordInput.attr("type") === "password") {
            accessPasswordInput.attr("type", "text");
            showPasswordBtnImg.attr("src", "assets/show-icon.png");
        } else {
            accessPasswordInput.attr("type", "password");
            showPasswordBtnImg.attr("src", "assets/hide-icon.png");
        }

        accessPasswordInput.focus();

    })

    // Keyboard keys
    for (let index = 0; index < aftertapKeys.length; index++) {
        const key = aftertapKeys.eq(index);
        const keyAftertapElem = $(`<div class="key-aftertap"></div>`);
        
        let keyHoldTimer, absoluteX, relativeX; 

        key.on("touchstart", () => {
            keyAftertapElem.text(key.text())
            key.append(keyAftertapElem);

            // Absolute position of the key
            absoluteX = key.offset().left;

            // Happens after half a second of holding the key.
            keyHoldTimer = setTimeout(() => {
                let newWidth;
                let oldWidth = keyAftertapElem.css("width");

                // Finds the alternate key and shows it if there is one
                let alternateKeys = findAlternateKey(keyAftertapElem.text());
                if (alternateKeys) {
                    alternateKeys = alternateKeys.split(" ")
                    typingAlternate = true;

                    newWidth = oldWidth;
                    
                    // Shifting the alternate keys if there are 2 of them,
                    // setting their width and handles the "L exception"
                    if (alternateKeys.length == 2) {
                        newWidth = Number(oldWidth.slice(0, oldWidth.length-2))*2+"px";
                        if (key.attr("data-char") === "l") {
                            keyAftertapElem.css("transform", "translateX(-25%) translateY(-25%)");
                        } else {
                            keyAftertapElem.css("transform", "translateX(25%) translateY(-25%)");
                        }
                    }

                    keyAftertapElem.css("background-color", "var(--colorkeyhold)")
                    keyAftertapElem.css("width", newWidth);
                    keyAftertapElem.empty()
                    
                    // Adds the alternate keys to the display
                    for (let index = 0; index < alternateKeys.length; index++) {
                        const character = alternateKeys[index];
                        const keyAlternateSelector = $(`<div class="key-alternate-selector"></div>`)
                        if (alternateKeys.length == 2) {
                            keyAlternateSelector.css("width", "40%");
                        }
                        if (key.attr("data-char") === "l") {
                            if (index === 1) {
                                keyAlternateSelector.css("background-color", "var(--colorkey)");
                            } 
                        } else if (index === 0) {
                            keyAlternateSelector.css("background-color", "var(--colorkey)");
                        } 
                        
                        keyAlternateSelector.text(character)
                        keyAftertapElem.append(keyAlternateSelector);
                    }
                }
            }, 400);
        });

        key.on("touchmove", (event) => {

            // Handling the selection of alternate keys,
            // if there are 2 or more of them
            if (keyAftertapElem.children().length !== 1) {

                let touch = event.originalEvent.touches[0];
                relativeX = touch.clientX - absoluteX;

                if (key.attr("data-char") === "l") {
                    relativeX = relativeX + 40;
                }
    
                keyAlternateSelectorIndex = Math.floor(relativeX / 40);
                
                // Highlighting the selecting alternate key
                for (let index = 0; index < keyAftertapElem.children().length; index++) {
                    const element = keyAftertapElem.children().eq(index);

                    if (index === 0) {
                        if (keyAlternateSelectorIndex <= index) {
                            element.css("background-color", "var(--colorkey)");
                        } else {
                            element.css("background-color", "transparent");
                        }
                    } else {
                        if (keyAlternateSelectorIndex >= index) {
                            element.css("background-color", "var(--colorkey)");
                        } else {
                            element.css("background-color", "transparent");
                        }
                    }  
                }
            }
        });

        key.on("touchend", () => {

            // Reseting everything
            keyAftertapElem.remove();
            clearInterval(keyHoldTimer)
            keyAftertapElem.css({
                "width": "calc(100%/10)",
                "transform": "translateY(-25%)",
                "background-color": "var(--colorkey)"
            });

            // Detecting the character to send
            keyToSend = key.attr("data-char");
            if (typingAlternate) {
                let alternateKeys = findAlternateKey(keyToSend).split(" ");
                if (alternateKeys.length == 1 || keyAlternateSelectorIndex <= 0) {
                    keyToSend = alternateKeys[0];
                } else if (keyAlternateSelectorIndex >= 1) {
                    keyToSend = alternateKeys[1];
                }

            }
            if (shiftState != 0) {
                keyToSend = keyToSend.toUpperCase();
            }

            console.log(keyToSend);

            // TODO: character sending

            typingAlternate = false;
        });

        
    }

    // Preventing the menu from showing up after
    // holding on a key with an image.
    for (let index = 0; index < keyboardKeys.length; index++) {
        const key = keyboardKeys.eq(index);

        key.on('contextmenu touchstart', function (e) {
            e.preventDefault(); 
        })
    }

    // Changing the keys to lower case depending
    // on the shift button state
    for (let index = 0; index < shiftAffectedKeys.length; index++) {
        const key = shiftAffectedKeys.eq(index);
        
        key.on("touchend", () => {
            if (shiftState == 1) {
                shiftState = 0;
                shiftKeyImg.attr("src", "assets/lower-case.png");
                for (let index = 0; index < shiftAffectedKeys.length; index++) {
                    const key = shiftAffectedKeys.eq(index);
                    key.text(key.text().toLowerCase())  
                }
            }
        });
    }

    // Switching between keyboards
    LToNKey.on("touchend", () => {
        keyboardLetters.css("display", "none");
        keyboardNumbers.css("display", "flex");
    });

    NToLKey.on("touchend", () => {
        keyboardLetters.css("display", "flex");
        keyboardNumbers.css("display", "none");
        keyboardSymbols.css("display", "none");
    });

    NToSKey.on("touchend", () => {
        keyboardNumbers.css("display", "none");
        keyboardSymbols.css("display", "flex");
    });

    SToNKey.on("touchend", () => {
        keyboardNumbers.css("display", "flex");
        keyboardSymbols.css("display", "none");
    });

    // Shift key handling
    shiftKey.on("touchend", () => {
        shiftState++;
        if (shiftState == 3) {
            shiftState = 0;
        }

        if (shiftState == 0) {
            shiftKeyImg.attr("src", "assets/lower-case.png");
            for (let index = 0; index < shiftAffectedKeys.length; index++) {
                const key = shiftAffectedKeys.eq(index);
        
                key.text(key.text().toLowerCase())
            }
        } else if (shiftState == 1) {
            shiftKeyImg.attr("src", "assets/upper-case.png");
            for (let index = 0; index < shiftAffectedKeys.length; index++) {
                const key = shiftAffectedKeys.eq(index);
        
                key.text(key.text().toUpperCase())
            }
        } else if (shiftState == 2) {
            shiftKeyImg.attr("src", "assets/caps-lock.png");
        }

        
    });

});
