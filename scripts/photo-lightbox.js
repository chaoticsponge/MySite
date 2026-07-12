(function () {
  const dialog = document.getElementById("photo-lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;

  const photos = Array.from(document.querySelectorAll(
    ".photo-grid img, .article-photo img, .article-photo-grid img"
  ));
  const viewerImage = dialog.querySelector(".lightbox-content");
  const count = dialog.querySelector(".lightbox-count");
  const closeButton = dialog.querySelector(".lightbox-close");
  const previousButton = dialog.querySelector(".lightbox-prev");
  const nextButton = dialog.querySelector(".lightbox-next");
  let currentIndex = 0;
  let touchStartX = 0;
  let touchStartY = 0;

  function preload(index) {
    const photo = photos[(index + photos.length) % photos.length];
    if (!photo) return;
    const image = new Image();
    image.src = photo.currentSrc || photo.src;
  }

  function show(index) {
    currentIndex = (index + photos.length) % photos.length;
    const photo = photos[currentIndex];
    const description = photo.alt || "Gallery photo";

    viewerImage.src = photo.currentSrc || photo.src;
    viewerImage.alt = description;
    count.textContent = `${currentIndex + 1} / ${photos.length}`;
    preload(currentIndex - 1);
    preload(currentIndex + 1);
  }

  function open(index) {
    show(index);
    dialog.showModal();
    closeButton.focus();
  }

  function close() {
    dialog.close();
  }

  photos.forEach(function (photo, index) {
    photo.tabIndex = 0;
    photo.setAttribute("role", "button");
    photo.setAttribute("aria-label", `View photo: ${photo.alt || index + 1}`);
    photo.addEventListener("click", function () { open(index); });
    photo.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        open(index);
      }
    });
  });

  closeButton.addEventListener("click", close);
  previousButton.addEventListener("click", function () { show(currentIndex - 1); });
  nextButton.addEventListener("click", function () { show(currentIndex + 1); });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) close();
  });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      show(currentIndex - 1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      show(currentIndex + 1);
    }
  });

  dialog.addEventListener("touchstart", function (event) {
    const touch = event.changedTouches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
  }, { passive: true });

  dialog.addEventListener("touchend", function (event) {
    const touch = event.changedTouches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    if (Math.abs(deltaX) < 50 || Math.abs(deltaX) < Math.abs(deltaY)) return;
    show(deltaX > 0 ? currentIndex - 1 : currentIndex + 1);
  }, { passive: true });

  dialog.addEventListener("close", function () {
    viewerImage.removeAttribute("src");
  });
})();
