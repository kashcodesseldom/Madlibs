(() => {
  "use strict";
  const layout = document.querySelector(".play-layout");
  if (!layout) return;

  const form = document.getElementById("play-form");
  const inputs = Array.from(form.querySelectorAll("input[name=answer]"));
  const track = layout.querySelector(".progress");
  const bar = layout.querySelector("[data-progress]");
  const barLabel = layout.querySelector("[data-progress-label]");
  const formError = form.querySelector("[data-form-error]");
  const submitBtn = form.querySelector("button[type=submit]");
  const total = inputs.length;

  // Preview elements, keyed by blank index
  const blankEls = new Map();
  const articleEls = new Map();
  layout.querySelectorAll("[data-preview] [data-blank]").forEach((el) => blankEls.set(Number(el.dataset.blank), el));
  layout.querySelectorAll("[data-preview] [data-article]").forEach((el) => {
    el.dataset.original = el.textContent;
    articleEls.set(Number(el.dataset.article), el);
  });

  // Silly word suggestions, matched on the blank's label (most specific first)
  const BANK = [
    ["plural noun", ["pickles", "sock puppets", "moon rocks", "spoons", "marshmallows", "tiny hats"]],
    ["verb ending in ing", ["yodeling", "juggling", "sneezing", "moonwalking", "slurping"]],
    ["verb past tense", ["tumbled", "giggled", "exploded", "wobbled", "sneezed"]],
    ["adjective", ["sparkly", "grumpy", "gigantic", "squishy", "fabulous", "soggy"]],
    ["adverb", ["dramatically", "sleepily", "wildly", "politely", "suspiciously"]],
    ["animal", ["llama", "hedgehog", "flamingo", "octopus", "goat"]],
    ["place", ["Bubble Beach", "the moon", "Noodle City", "Tulip Lane"]],
    ["food", ["spaghetti", "pancakes", "meatballs", "waffles", "pickles"]],
    ["body part", ["elbow", "eyebrow", "knee", "left ear", "big toe"]],
    ["color", ["lavender", "tangerine", "magenta", "teal", "peach"]],
    ["name", ["Gertrude", "Bartholomew", "Zippy", "Mabel", "Fitz"]],
    ["number", ["7", "42", "113", "1,000", "12"]],
    ["emotion", ["giddy", "nervous", "thrilled", "embarrassed", "sleepy"]],
    ["silly word", ["bazinga", "flibbertigibbet", "wiggle-waggle", "snorkelbop", "kerfuffle"]],
    ["exclamation", ["Yikes", "Hooray", "Great Scott", "Holy moly", "Oops"]],
    ["sound", ["honk", "squeak", "kaboom", "splat", "boing"]],
    ["vehicle", ["scooter", "tractor", "hot-air balloon", "skateboard", "canoe"]],
    ["occupation", ["baker", "pilot", "detective", "plumber", "magician"]],
    ["liquid", ["lemonade", "gravy", "orange juice", "maple syrup", "chocolate milk"]],
    ["room", ["kitchen", "attic", "bathroom", "garage", "library"]],
    ["verb", ["wiggle", "juggle", "hiccup", "shimmy", "tiptoe"]],
    ["noun", ["umbrella", "trombone", "potato", "waffle iron", "teapot"]],
  ];
  const FALLBACK = ["banana", "wobbly", "zigzag", "kazoo", "fluffy"];

  function suggest(label, current) {
    const entry = BANK.find(([key]) => label.includes(key));
    const options = (entry ? entry[1] : FALLBACK).filter((w) => w !== current);
    return options[Math.floor(Math.random() * options.length)];
  }

  function articleFor(original, word) {
    const base = /^[aeiou]/i.test(word) ? "an" : "a";
    return original[0] === original[0].toUpperCase() ? base[0].toUpperCase() + base.slice(1) : base;
  }

  function refresh(i) {
    const word = inputs[i].value.trim();
    const blank = blankEls.get(i);
    blank.textContent = word || blank.dataset.label;
    blank.classList.toggle("filled", Boolean(word));
    const art = articleEls.get(i);
    if (art) art.textContent = word ? articleFor(art.dataset.original, word) : art.dataset.original;
  }

  function updateProgress() {
    const filled = inputs.filter((el) => el.value.trim()).length;
    bar.style.width = `${(filled / total) * 100}%`;
    track.setAttribute("aria-valuenow", filled);
    barLabel.textContent = `${filled} of ${total} words filled`;
  }

  function setValue(i, value) {
    inputs[i].value = value;
    clearFieldError(i);
    refresh(i);
    updateProgress();
  }

  function showFieldError(i, message) {
    const field = inputs[i].closest(".field");
    field.classList.add("invalid");
    field.querySelector(".field-error").textContent = message;
    inputs[i].setAttribute("aria-invalid", "true");
  }

  function clearFieldError(i) {
    const field = inputs[i].closest(".field");
    field.classList.remove("invalid");
    field.querySelector(".field-error").textContent = "";
    inputs[i].removeAttribute("aria-invalid");
  }

  inputs.forEach((input, i) => {
    input.addEventListener("input", () => {
      clearFieldError(i);
      refresh(i);
      updateProgress();
    });
    // Enter moves to the next blank; on the last one it submits
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && i < total - 1) {
        event.preventDefault();
        inputs[i + 1].focus();
      }
    });
  });

  form.addEventListener("click", (event) => {
    const dice = event.target.closest("[data-random]");
    if (dice) {
      const i = inputs.indexOf(dice.closest(".field").querySelector("input"));
      setValue(i, suggest(inputs[i].dataset.label, inputs[i].value));
      return;
    }
    if (event.target.closest("[data-fill-random]")) {
      inputs.forEach((input, i) => {
        if (!input.value.trim()) setValue(i, suggest(input.dataset.label, ""));
      });
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    inputs.forEach((_, i) => clearFieldError(i));
    formError.textContent = "";

    const answers = inputs.map((el) => el.value.trim());
    const empty = answers.map((a, i) => (a ? -1 : i)).filter((i) => i >= 0);
    if (empty.length) {
      empty.forEach((i) => showFieldError(i, "Add a word here."));
      formError.textContent = empty.length === 1 ? "1 blank is still empty." : `${empty.length} blanks are still empty.`;
      inputs[empty[0]].focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Reading...";
    try {
      const res = await fetch(layout.dataset.submitUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.result_url) {
        window.location.assign(data.result_url);
        return;
      }
      Object.entries(data.fields || {}).forEach(([i, message]) => showFieldError(Number(i), message));
      formError.textContent = data.error || "Something went wrong. Try again.";
    } catch (err) {
      formError.textContent = "Couldn't reach the server. Check your connection and try again.";
    }
    submitBtn.disabled = false;
    submitBtn.textContent = "Read my story";
  });
})();
