const socket = io();

socket.on("add_lurker", (user) => {
    console.log("New lurking user: " + user);
    const lurkingDiv = document.getElementById("lurking-div");
    const lurkingList = lurkingDiv.querySelector(".lurking-list");
    lurkingList.innerHTML += `<li>${user}</li>`;
});

socket.on("remove_lurker", (user) => {
    console.log("Lurker left: " + user);
    const lurkingDiv = document.getElementById("lurking-div");
    const lurkingList = lurkingDiv.querySelector(".lurking-list");
    lurkingList.innerHTML = lurkingList.innerHTML.replace(
        `<li>${user}</li>`,
        ""
    );
})