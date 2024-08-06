(() => {
  function nothing() {}

  function load(src, callback) {
    let script = document.createElement('script');
    script.async = true;
    script.onload = callback;
    script.src = src;
    document.head.appendChild(script);
  }

  function math() {
    window.MathJax = {
      showMathMenu: false,
      showProcessingMessages: false,
      // displayAlign: "left",
      jax: ["input/TeX","input/MathML","output/CommonHTML"],
      messageStyle: "none",
      extensions: ["tex2jax.js","mml2jax.js","MathZoom.js","AssistiveMML.js", "a11y/accessibility-menu.js"],
      TeX: {
        extensions: ["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"]
      }
    };
    load("//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js", nothing);
  }

  function init_han() {
    load("/assets/han.min.js", () => {
      Han(document).initCond()
      // .renderElem()
      //.renderHanging()
      //.renderJiya()
      .renderHWS()
      // .correctBasicBD()
      // .substCombLigaWithPUA();
    });
  }

  console.log("Whoa!  (*~・ω・)~ https://github.com/quanbrew");
  init_han();

  function shuffle_list(selector) {

    // https://stackoverflow.com/questions/7070054/javascript-shuffle-html-list-element-order
    let ul = document.querySelector(selector);
    if (ul !== null && ul.children !== null) {
      for (let i = ul.children.length; i >= 0; i--) {
          ul.appendChild(ul.children[Math.random() * i | 0]);
      }
    }
  }

  function ready() {
    // On-demand loading
    const code_blocks = document.querySelectorAll('code[class*="language-"], pre[class*="language-"]');
    const math_blocks = document.querySelectorAll('script[type*="math"]');
    // if (code_blocks.length !== 0) {
      load("/assets/prism.js", nothing);
    // }
    // if (math_blocks.length !== 0) {

    // }

    // Shuffle the friendship links
    shuffle_list('.friendship-links');
  }
  math();
  if (document.readyState !== 'loading') {
    ready();
  } else {
    document.addEventListener('DOMContentLoaded', ready);
  }
})();
