document.addEventListener("DOMContentLoaded", function () {
  setInterval(() => {
    window.location.href = window.location.href;
  }, 3000); // horribly inefficient; but it works, so it isnt that bad, right?
  window.location.href = window.location.href;
});
