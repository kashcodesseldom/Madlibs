(() => {
  "use strict";
  const root = document.querySelector("[data-result]");
  if (!root) return;

  // Reveal the player's words one by one (skipped for reduced motion)
  const story = root.querySelector(".story-final");
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!calm) {
    story.querySelectorAll("mark.word").forEach((el, i) => el.style.setProperty("--i", i));
    story.classList.add("reveal");
  }

  // Copy the share link
  const button = root.querySelector("[data-copy-link]");
  const status = root.querySelector("[data-copy-status]");

  function fallbackCopy(text) {
    const box = document.createElement("textarea");
    box.value = text;
    box.style.position = "fixed";
    box.style.opacity = "0";
    document.body.appendChild(box);
    box.select();
    const ok = document.execCommand("copy");
    box.remove();
    return ok;
  }

  button.addEventListener("click", async () => {
    const url = button.dataset.url;
    let copied = false;
    try {
      await navigator.clipboard.writeText(url);
      copied = true;
    } catch (err) {
      copied = fallbackCopy(url);
    }
    status.textContent = copied ? "Link copied. Send it to a friend." : `Copy this link: ${url}`;
  });
})();
