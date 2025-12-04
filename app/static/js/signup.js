// Tooltip initialization
document.querySelectorAll('[data-bs-toggle="tooltip"]')
  .forEach(el => new bootstrap.Tooltip(el));

// Toggle password visibility
function togglePass(id, icon) {
  const input = document.getElementById(id);
  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";
  icon.textContent = isHidden ? "visibility_off" : "visibility";
}

// Validation logic
const password = document.getElementById("password");
const confirm = document.getElementById("confirm");
const signupBtn = document.getElementById("signupBtn");

let captchaVerified = false;

function validate() {
  const p = password.value;
  const c = confirm.value;
  const strong = /^[A-Z]/.test(p) && p.length >= 7 && /[^A-Za-z0-9]/.test(p);
  signupBtn.disabled = !(strong && p === c && captchaVerified);
}

password.addEventListener("input", validate);
confirm.addEventListener("input", validate);

// reCAPTCHA callback
function onCaptchaSuccess() {
  captchaVerified = true;
  validate();
}
