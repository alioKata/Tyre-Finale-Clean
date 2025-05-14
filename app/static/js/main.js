let currentIndex = 0;
let isAnimating = false;
const animationDuration = 500;

document.addEventListener("DOMContentLoaded", () => {
  const boxes = document.querySelectorAll(".carousel-box");
  const dots = document.querySelectorAll(".step-dot");
  const prevBtn = document.querySelector(".nav-button.prev");
  const nextBtn = document.querySelector(".nav-button.next");
  const uploadBtn = document.getElementById("uploadButton");
  const fileInput = document.getElementById("fileInput");

  // Check if user is authenticated
  const userEmail = localStorage.getItem("userEmail");
  if (!userEmail) {
    // Redirect to registration if not authenticated
    window.location.href = "/register";
    return;
  }

  // Generate and display a random percentage for demo purposes
  function setupDemoChart() {
    const randomPercentage = Math.floor(Math.random() * 101); // 0-100
    const chartEl = document.querySelector(".circular-progress");
    const textEl = document.querySelector(".progress-text");

    if (chartEl && textEl) {
      const angle = (randomPercentage / 100) * 360;
      chartEl.style.background = `conic-gradient(#1877f2 0deg ${angle}deg, #ccc ${angle}deg 360deg)`;
      textEl.textContent = `${randomPercentage}%`;
    }
  }

  function init() {
    boxes.forEach((box, idx) => {
      box.style.display = idx === currentIndex ? "flex" : "none";
      box.style.opacity = idx === currentIndex ? "1" : "0";
    });
    updateDots();
    toggleNav();
    setupDemoChart(); // Initialize chart with random value
  }

  function navigateTo(idx) {
    if (isAnimating || idx < 0 || idx >= boxes.length) return;
    isAnimating = true;
    boxes[currentIndex].style.opacity = "0";
    boxes[idx].style.display = "flex";
    setTimeout(() => {
      boxes[currentIndex].style.display = "none";
      boxes[idx].style.opacity = "1";
      currentIndex = idx;
      updateDots();
      toggleNav();
      isAnimating = false;
    }, animationDuration);
  }

  function updateDots() {
    dots.forEach((dot, idx) => {
      dot.classList.toggle("active", idx === currentIndex);
    });
  }

  function toggleNav() {
    prevBtn.style.visibility = currentIndex === 0 ? "hidden" : "visible";
    nextBtn.style.visibility = currentIndex === boxes.length - 1 ? "hidden" : "visible";
  }

  function showProcessingAlert() {
    const alertDiv = document.createElement("div");
    alertDiv.className = "processing-alert";
    alertDiv.innerHTML = `
      <div class="alert-content">
        <p>Machine learning model is processing your image.<br>Wait for the estimation.</p>
        <div class="spinner"><span class="gear">⚙️</span></div>
      </div>`;
    document.body.appendChild(alertDiv);
  }

  prevBtn.addEventListener("click", () => navigateTo(currentIndex - 1));
  nextBtn.addEventListener("click", () => navigateTo(currentIndex + 1));
  dots.forEach((dot, idx) => dot.addEventListener("click", () => navigateTo(idx)));

  uploadBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    showProcessingAlert();
    const form = new FormData();
    form.append("file", file);
    form.append("userEmail", userEmail); // Add user email to form data

    try {
      const res = await fetch("/api/tire/upload", {
        method: "POST",
        body: form,
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Upload failed");

      // Store the complete record
      localStorage.setItem("latestTireRecord", JSON.stringify(json));

      // Also store the RUL value separately for backward compatibility
      localStorage.setItem("rul", json.rul_percent);

      setTimeout(() => window.location.href = "/result", 1000);
    } catch (err) {
      alert("Error: " + err.message);
      document.getElementById("fileInput").value = "";
      document.querySelector(".processing-alert")?.remove();
    }
  });

  init();
});
