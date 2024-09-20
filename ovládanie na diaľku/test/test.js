$(document).ready(() => {
    const input = $("#input");
    const inputText = $(".input-text");

    input.val(" ")

    input.on("input", () => {
        let inputValue = input.val();
        let currentText = inputText.text();
        
        if (inputValue === "") {
            inputText.text(currentText.slice(0, currentText.length - 1))
        } else {
            inputText.text(currentText + input.val().slice(1))
        }
        
        input.val(" ")
    })

});