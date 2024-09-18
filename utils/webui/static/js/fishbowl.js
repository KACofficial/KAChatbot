document.addEventListener("DOMContentLoaded", () => {
  const socket = io();

  socket.on("update_fishbowl", (fishList) => {
    console.log(fishList);
    const aquarium = document.getElementById("aquarium");

    const currentFishElements = aquarium.querySelectorAll(".fish");
    const currentFishSet = new Set(
      Array.from(currentFishElements).map(
        (fish) => fish.querySelector(".fish-name").textContent
      )
    );

    currentFishElements.forEach((fish) => {
      if (
        !fishList.some(
          (newFish) =>
            newFish.name === fish.querySelector(".fish-name").textContent
        )
      ) {
        aquarium.removeChild(fish);
      }
    });

    fishList.forEach((fish) => {
      if (!currentFishSet.has(fish.name)) {
        const fishDiv = document.createElement("div");
        fishDiv.className = "fish";
        fishDiv.innerHTML = `
          <p class="fish-name">${fish.name}</p>
          <img src="/static/assets/${fish.image}.png" class="fish-image" />
        `;
        // Set initial position from server
        fishDiv.style.left = `${fish.position.x}px`;
        fishDiv.style.top = `${fish.position.y}px`;

        if (fish.color) {
          const fishNameElement = fishDiv.querySelector(".fish-name");
          if (fishNameElement) {
            fishNameElement.style.color = fish.color;
          }
        }

        aquarium.appendChild(fishDiv);

        startFishMovement(fishDiv);
      }
    });
  });

  function moveFishContainer(fishContainer) {
    const aquarium = document.getElementById("aquarium");

    if (!aquarium) return;

    const aquariumWidth = aquarium.clientWidth;
    const aquariumHeight = aquarium.clientHeight;

    const fishContainerWidth = fishContainer.clientWidth;
    const fishContainerHeight = fishContainer.clientHeight;

    const currentX = parseFloat(fishContainer.style.left) || 0;
    const currentY = parseFloat(fishContainer.style.top) || 0;

    const movementRangeX = 500;
    const movementRangeY = 500;

    // Define buffer from the walls to stop fish from going too close
    const wallBuffer = 50;

    // Calculate new position, ensuring they don't move towards the walls
    let randomX = currentX + (Math.random() - 0.5) * movementRangeX;
    let randomY = currentY + (Math.random() - 0.5) * movementRangeY;

    // Prevent fish from going towards the left wall
    if (currentX < wallBuffer) {
      randomX = Math.max(currentX, currentX + Math.random() * movementRangeX);
    }

    // Prevent fish from going towards the right wall
    if (currentX > aquariumWidth - fishContainerWidth - wallBuffer) {
      randomX = Math.min(currentX, currentX - Math.random() * movementRangeX);
    }

    // Prevent fish from going towards the top wall
    if (currentY < wallBuffer) {
      randomY = Math.max(currentY, currentY + Math.random() * movementRangeY);
    }

    // Prevent fish from going towards the bottom wall
    if (currentY > aquariumHeight - fishContainerHeight - wallBuffer) {
      randomY = Math.min(currentY, currentY - Math.random() * movementRangeY);
    }

    randomX = Math.max(
      0,
      Math.min(aquariumWidth - fishContainerWidth, randomX)
    );
    randomY = Math.max(
      0,
      Math.min(aquariumHeight - fishContainerHeight, randomY)
    );

    // Determine if the fish should be flipped
    const shouldFlip = randomX < currentX;

    fishContainer.style.left = `${randomX}px`;
    fishContainer.style.top = `${randomY}px`;

    const fishImage = fishContainer.querySelector(".fish-image");
    if (fishImage) {
      fishImage.style.transform = shouldFlip ? "scaleX(1)" : "scaleX(-1)";
    }
  }

  function startFishMovement(fishContainer) {
    function scheduleMovement() {
      moveFishContainer(fishContainer);

      const interval = Math.random() * 5000 + 5000; // Between 5s and 10s
      setTimeout(scheduleMovement, interval);
    }

    setTimeout(scheduleMovement, 0);
  }

  const observer = new MutationObserver(() => {
    const fishContainers = document.querySelectorAll(".fish");
    fishContainers.forEach((fishContainer) => {
      if (!fishContainer.hasAttribute("data-moving")) {
        fishContainer.setAttribute("data-moving", "true");
        startFishMovement(fishContainer);
      }
    });
  });

  const aquarium = document.getElementById("aquarium");
  if (aquarium) {
    observer.observe(aquarium, { childList: true });
  }
});
