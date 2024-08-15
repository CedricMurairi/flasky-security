function checkPasswordValidity() {
    const passwordInput = document.querySelector('#password')
    const passwordRequirements = document.querySelectorAll('.password-requirement')

    if (!passwordInput) {
        return
    }

    passwordInput.addEventListener('input', () => {
        const passwordValue = passwordInput.value

        passwordRequirements.forEach((requirement, index) => {
            if (checkRequirement(passwordValue, index)) {
                requirement.style.color = 'green'
            } else {
                requirement.style.color = 'red'
            }
        })
    })

    function checkRequirement(password, index) {
        switch (index) {
            case 0:
                return password.length >= 8
            case 1:
                return /[A-Z]/.test(password)
            case 2:
                return /[a-z]/.test(password)
            case 3:
                return /\d/.test(password)
            case 4:
                return /[!@#$%^&*]/.test(password)
            default:
                return false
        }
    }
}

checkPasswordValidity()

function toggleReplyForm(commentID) {
    const replyForm = document.querySelector(`#comment-form-${commentID}`)

    if (replyForm.style.display === 'block') {
        replyForm.style.display = 'none';
        return;
    }
    replyForm.style.display = 'block';
}

function toggleRepliesBlock(commentID) {
    const replyForm = document.querySelector(`#replies-block-${commentID}`)

    if (replyForm.style.display === 'block') {
        replyForm.style.display = 'none';
        return;
    }
    replyForm.style.display = 'block';
}

function togglePasswordVisibility() {
    var x = document.getElementById("password");
    var y = document.getElementById("pass_toggle_label");
    if (x.type === "password") {
        x.type = "text";
        y.innerHTML = "Hide password";
    } else {
        x.type = "password";
        y.innerHTML = "Show password";
    }
} 