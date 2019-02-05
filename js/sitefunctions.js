function initCloseBtn() {
      var closeEl = document.querySelector(".close");
      if (closeEl) {
        closeEl.addEventListener('click', function() {
          window.close();
        });
      };
      return closeEl;
}

document.addEventListener('DOMContentLoaded', function() {
  initCloseBtn();
});
