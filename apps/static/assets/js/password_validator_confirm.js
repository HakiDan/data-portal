addEventListener("DOMContentLoaded", (event) => {
    const passwordAlert = document.getElementById("password-alert-2");
    const requirements = document.querySelectorAll(".requirements2");
    const password = document.getElementById("new_password1");
    const password2 = document.getElementById("new_password2");
    let matchBoolean;
    let match = document.querySelector(".match2");

    requirements.forEach((element) => element.classList.add("wrong"));

    password2.addEventListener("focus", () => {
        passwordAlert.classList.remove("d-none");
        if (!password2.classList.contains("is-valid")) {
            password2.classList.add("is-invalid");
        }
    });

    password2.addEventListener("input", () => {
        let value = password.value;
        let value2 = password2.value;
        if (value2 === null) {
            matchBoolean = false;
        }
        else {
            if (value == value2) {
                matchBoolean = true;
            } 
            else {
                matchBoolean = false;
            }
        }

        if (matchBoolean == true) {
            password2.classList.remove("is-invalid");
            password2.classList.add("is-valid");

            requirements.forEach((element) => {
                element.classList.remove("wrong");
                element.classList.add("good");
            });
            passwordAlert.classList.remove("alert-warning");
            passwordAlert.classList.add("alert-success");
        } else {
            password2.classList.remove("is-valid");
            password2.classList.add("is-invalid");

            passwordAlert.classList.add("alert-warning");
            passwordAlert.classList.remove("alert-success");

            if (matchBoolean == false) {
                match.classList.add("wrong");
                match.classList.remove("good");
            } else {
                match.classList.add("good");
                match.classList.remove("wrong");
            }
        }
    });

    password2.addEventListener("blur", () => {
        passwordAlert.classList.add("d-none");
    });
});