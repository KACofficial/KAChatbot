const socket = io();

function getQueryParam(param) {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  return urlParams.get(param);
}

function parseParams(channel = "all", date = "") {
  console.log(`Requesting chatlog for channel: ${channel}, date: ${date}`);
  socket.emit("request_chatlog", { channel: channel, date: date });
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded");

  // Ensure the socket is connected before listening for events
  socket.on("connect", () => {
    console.log("Socket connected");

    // Request chatlog once connected
    const channel = getQueryParam("channel") || "all"; // Default to "all" if not provided
    const date = getQueryParam("date") || ""; // Default to empty string if not provided

    // Ensure both channel and date are valid before emitting the request
    parseParams(channel, date);
    setInterval(() => parseParams(channel, date), 2000);

    socket.on("update_chatlog", (data) => {
      console.log("Received data:", data);

      const chatlogDiv = document.getElementById("chatlog-div");

      // Clear existing chatlog items
      chatlogDiv.innerHTML = "";

      // Check if data and channels exist
      if (data && data.channels && Object.keys(data.channels).length > 0) {
        console.log("Data and channels exist");
        let hasMessages = false;

        Object.entries(data.channels).forEach(([channel, channelData]) => {
          // console.log(`Processing channel: ${channel}`, channelData); // Log channel data

          // Create channel section
          const channelDiv = document.createElement("div");
          channelDiv.className = "chat-channel";

          const channelHeading = document.createElement("h2");
          channelHeading.textContent = channel;
          channelDiv.appendChild(channelHeading);

          if (channelData.chatlog && channelData.chatlog.length > 0) {
            hasMessages = true;

            channelData.chatlog.forEach((message) => {
              console.log(`Processing message:`, message); // Log each message

              // Create message section
              const messageDiv = document.createElement("div");
              messageDiv.className = "chat-message";

              const timestampSpan = document.createElement("span");
              timestampSpan.className = "timestamp";
              timestampSpan.textContent = message.timestamp;
              messageDiv.appendChild(timestampSpan);

              if (message.badges) {
                Object.entries(message.badges).forEach(([badge, value]) => {
                  console.log(
                    `Processing badge: ${badge} with value: ${value}`
                  ); // Log badge data

                  const badgeSpan = document.createElement("span");
                  badgeSpan.className = `badge ${badge}`;
                  badgeSpan.textContent = badge;
                  messageDiv.appendChild(badgeSpan);
                });
              }

              const usernameSpan = document.createElement("span");
              usernameSpan.className = "username";
              usernameSpan.textContent = `${message.username}: `;
              messageDiv.appendChild(usernameSpan);

              const messageSpan = document.createElement("span");
              messageSpan.className = "message";
              messageSpan.textContent = message.message;
              messageDiv.appendChild(messageSpan);

              channelDiv.appendChild(messageDiv);
            });
          } else {
            const noMessagesParagraph = document.createElement("p");
            noMessagesParagraph.textContent =
              "No messages available for this channel.";
            channelDiv.appendChild(noMessagesParagraph);
          }

          chatlogDiv.appendChild(channelDiv);
        });

        if (!hasMessages) {
          const noChatlogsParagraph = document.createElement("p");
          noChatlogsParagraph.textContent =
            "No chat logs available for the selected date.";
          chatlogDiv.appendChild(noChatlogsParagraph);
        }
      } else {
        const noChatlogsParagraph = document.createElement("p");
        noChatlogsParagraph.textContent =
          "No chat logs available for the selected date.";
        chatlogDiv.appendChild(noChatlogsParagraph);
      }
    });
  });
});
