const socket = io();

const generateDeleteSVG = (id) => `
    <svg class="delete-btn" onclick="deleteItem(this, '${id}')" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
    </svg>`;

socket.on("add_lurker", (user) => {
  console.log("New lurking user: " + user);
  const lurkingDiv = document.getElementById("lurking-div");
  const lurkingList = lurkingDiv.querySelector(".lurking-list");

  // Create a unique ID for the list item
  const id = `lurker-${user}`;
  lurkingList.innerHTML += `<li data-id="${id}">${user}${generateDeleteSVG(
    id
  )}</li>`;
});

socket.on("remove_lurker", (user) => {
  console.log("Lurker left: " + user);
  const lurkingDiv = document.getElementById("lurking-div");
  const lurkingList = lurkingDiv.querySelector(".lurking-list");

  // Remove the list item with the corresponding data-id
  const id = `lurker-${user}`;
  const item = lurkingList.querySelector(`[data-id="${id}"]`);
  if (item) {
    item.remove();
  }
});

socket.on("add_song_request", (song) => {
  console.log("song request: " + song);
  const songsDiv = document.getElementById("songs-div");
  const songList = songsDiv.querySelector(".song-list");

  // Create a unique ID for the song request
  const id = `song-${song}`;
  songList.innerHTML += `<li data-id="${id}">${song}${generateDeleteSVG(
    id
  )}</li>`;
});

function deleteItem(svg, id) {
  console.log("deleteItem called with id:", id);
  console.log("SVG onclick attribute:", svg.getAttribute("onclick")); // Verify the onclick attribute is correct
  console.log("SVG element:", svg); // Check the SVG element itself

  const li = svg.closest("li");
  console.log("Closest <li> element:", li); // Check if closest <li> is correctly selected

  if (li) {
    console.log("LI data-id attribute:", li.getAttribute("data-id")); // Check the data-id of the <li>
    if (li.getAttribute("data-id") === id) {
      // Determine the list type based on the parent <ul> or <ol> class
      let listType = "";
      const parentList = li.closest("ul") || li.closest("ol"); // Check both <ul> and <ol>
      if (parentList) {
        if (parentList.classList.contains("lurking-list")) {
          listType = "lurkers";
        } else if (parentList.classList.contains("song-list")) {
          listType = "songs";
        }
      }

      console.log("Determined list type:", listType); // Print the determined list type

      // Emit the event with list type and item id
      socket.emit("remove_item", { listType, itemId: id });
      li.remove(); // Remove the item from the list
    } else {
      console.error(
        "ID mismatch: expected",
        id,
        "but found",
        li.getAttribute("data-id")
      ); // Print error if IDs don't match
    }
  } else {
    console.error("No <li> element found."); // Print error if <li> is not found
  }
}
