const formElement = document.querySelector("#form");
formElement.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(formElement);

    const submitButton = formElement.querySelector("button[type=submit]");
    submitButton.disabled = true;
    const loadingElement = document.createElement("div");
    loadingElement.innerText = "Loading...";
    form.append(loadingElement);

    fetch("/api/send-email", {
        method: "POST",
        body: formData,
    })
        .then((res) => {
            if (res.ok) {
                formElement.reset();
                alert("Email sent successfully!");
            }
            else {
                alert("Error sending email!");
            }
        })
        .catch((err) => {
            alert("Error sending email!\n" + err);
        })
        .finally(() => {
            submitButton.disabled = false;
            loadingElement.remove();
        });
});