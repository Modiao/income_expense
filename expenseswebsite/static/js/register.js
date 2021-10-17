const usernameField = document.querySelector('#usernameField');
const feedbackField = document.querySelector('.invalid_feedback');
const emailField = document.querySelector('#emailField');
const passwordField = document.querySelector('#passwordField');
const passwordField1 = document.querySelector('#passwordField1');
const emailFeedbackArea = document.querySelector('.emailFeedbackArea');
const usernameSuccessArea = document.querySelector('.usernameSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submitBtn');


const handleToggleInput = (e) => {

    if (showPasswordToggle.textContent == "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);

usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameField.classList.remove('is-invalid');
    feedbackField.style.display = "none";
    usernameSuccessArea.style.display = "block";
    usernameSuccessArea.textContent = `Checking ${usernameVal}`;

    if (usernameVal.length > 0) {
        fetch("/authentication/validate-username", {
                body: JSON.stringify({ username: usernameVal }),
                method: "POST",
            })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data)
                usernameSuccessArea.style.display = "none";
                if (data.username_error) {
                    usernameField.classList.add('is-invalid');
                    feedbackField.style.display = "block";
                    feedbackField.innerHTML = `<p>${data.username_error}</p>`;
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute('disabled');
                }
            });
    }
});


emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove('is-invalid');
    emailFeedbackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/authentication/validate-email", {
                body: JSON.stringify({ email: emailVal }),
                method: "POST",
            })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data)
                if (data.email_error) {
                    emailField.classList.add('is-invalid');
                    emailFeedbackArea.style.display = "block";
                    emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute('disabled');
                }
            });
    }
});