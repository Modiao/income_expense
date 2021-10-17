const showPasswordToggle1 = document.querySelector('.showPasswordToggle1');


const handleToggleInput1 = (e) => {

    if (showPasswordToggle1.textContent == "SHOW") {
        showPasswordToggle1.textContent = "HIDE";
        passwordField1.setAttribute("type", "text");
    } else {
        showPasswordToggle1.textContent = "SHOW";
        passwordField1.setAttribute("type", "password");
    }
};

showPasswordToggle1.addEventListener('click', handleToggleInput1);