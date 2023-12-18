var sdk = apigClientFactory.newClient({});

const groups = [
  {
    //THIS IS USED FOR TESTING
    groupId: 1,
    groupLeader: {
      userId: 1,
      userName: "test1",
      userFeatures: [
        { featureName: "Feature 1", featureValue: "1Value 1" },
        { featureName: "Feature 2", featureValue: "1Value 2" },
      ],
    },
    groupMembers: [
      {
        userId: 1,
        userName: "test1",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "1Value 1" },
          { featureName: "Feature 2", featureValue: "1Value 2" },
        ],
      },
      {
        userId: 2,
        userName: "test2",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "2Value 1" },
          { featureName: "Feature 2", featureValue: "2Value 2" },
        ],
      },
      {
        userId: 3,
        userName: "test3",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "3Value 1" },
          { featureName: "Feature 2", featureValue: "3Value 2" },
        ],
      },
    ],
  },
  {
    groupId: 2,
    groupLeader: {
      userId: 2,
      userName: "test2",
      userFeatures: [
        { featureName: "Feature 1", featureValue: "2Value 1" },
        { featureName: "Feature 2", featureValue: "2Value 2" },
      ],
    },
    groupMembers: [
      {
        userId: 3,
        userName: "test3",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "3Value 1" },
          { featureName: "Feature 2", featureValue: "3Value 2" },
        ],
      },
      {
        userId: 2,
        userName: "test2",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "2Value 1" },
          { featureName: "Feature 2", featureValue: "2Value 2" },
        ],
      },
    ],
  },
];

const invites = [
  {
    invitingGroup: groups[0],
    invitee: {
      userId: 1,
      userName: "test1",
      userFeatures: [
        { featureName: "Feature 1", featureValue: "1Value 1" },
        { featureName: "Feature 2", featureValue: "1Value 2" },
      ],
    },
  },
  {
    invitingGroup: groups[1],
    invitee: {
      userId: 1,
      userName: "test1",
      userFeatures: [
        { featureName: "Feature 1", featureValue: "1Value 1" },
        { featureName: "Feature 2", featureValue: "1Value 2" },
      ],
    },
  },
];

async function callChatPostApi(send, group_id, user_id, message) {
  params = {};
  body = { send: send, group_id: group_id, user_id: user_id, message: message };
  additionalParams = {};
  chatLogs = sdk.chatPost(params, body, additionalParams);
  console.log("CHAT LOGS: " + JSON.stringify(chatLogs));
  return chatLogs;
}

function callProfilePostApi(user_id) {
  //Should return an object containing user groups, name, features, and pending invites
  var params = {};
  var body = { userId: user_id };
  var additionalParams = {};
  sdk.profilePost(params, body, additionalParams).then((userInfo) => {
    const userGroups = userInfo.data.groups;
    var ledGroups = [];
    for (let i = 0; i < userGroups.length; i++) {
      if (userGroups[i].groupLeader.userId == user_id) {
        ledGroups.push(userGroups[i].groupId);
      }
    }
    localStorage.setItem("_ledGroups", btoa(JSON.stringify(ledGroups)));
    localStorage.setItem("_userFeatures", btoa(JSON.stringify(userInfo.data.userFeatures)));
    localStorage.setItem("_userGroups", btoa(JSON.stringify(userInfo.data.groups)));
    localStorage.setItem("_userInvites", btoa(JSON.stringify(userInfo.data.pendingInvites)));
    console.log("Updated");
  });
}

function callGroupPutApi(user_id, group_leader_id, group_id) {
  if (user_id == group_leader_id) {
    params = {};
    body = { group_id: group_id };
    additionalParams = {};
    alert("Group deleted. Please wait a few moments to see this update here.");
    return sdk.groupPut(params, body, additionalParams);
  }
  console.log("You cannot delete this group because you are not the group leader");
  return "You cannot delete this group because you are not the group leader";
}

function callGroupPostApi(user_id, group_members) {
  params = {};
  body = { groupLeader: user_id, groupMembers: group_members };
  additionalParams = {};
  alert("Group created. You can now invite new members! Please wait a few moments to see this update here.");
  return sdk.groupPost(params, body, additionalParams);
}

function callRespondToInvitationPostApi(invitationResponse) {
  console.log(invitationResponse);
  params = {};
  body = invitationResponse;
  additionalParams = {};
  return sdk.respondToInvitationPost(params, body, additionalParams);
}

function openGroupTab(tabName) {
  var i, x;
  x = document.getElementsByClassName("groupDetails");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  document.getElementById(tabName).style.display = "block";
}

function openInviteTab(tabName) {
  var i, x;
  x = document.getElementsByClassName("inviteDetails");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  document.getElementById(tabName).style.display = "block";
}

async function openChatWindow(groupId, user_id, first_name) {
  var chatWindow = document.getElementById("chatWindow");
  var chatMain = document.getElementById("chatMain");
  chatMain.setAttribute("data-groupId", groupId);
  // delete all children of chatMain
  while (chatMain.firstChild) {
    chatMain.removeChild(chatMain.firstChild);
  }

  if (chatWindow.style.display === "none") {
    chatWindow.style.display = "block";
  }
  callChatPostApi(0, chatMain.getAttribute("data-groupId"), user_id, "").then((chatLogs) => {
    console.log("CHAT LOGS2: " + JSON.stringify(chatLogs));
    for (let i = 0; i < chatLogs.data.length; i++) {
      var chatLog = chatLogs.data[i];
      var message = chatLog[0];
      var sender = chatLog[1];
      var side = "left";
      if (sender == first_name) {
        side = "right";
        sender = "Me";
      }
      console.log("TESTING: " + side + " " + sender);
      speak(sender, side, message);
    }
  });
  var title = document.getElementById("chatTitle");
  title.innerHTML = "Group " + groupId + " Chat";
}

function speak(name, side, text) {
  const chat = document.getElementById("chatMain");
  const msg = `
      <div class="msg ${side}-msg">
  
        <div class="msg-bubble">
          <div class="msg-info">
            <div class="msg-info-name">${name}</div>
          </div>
  
          <div class="msg-text">${text}</div>
        </div>
      </div>
    `;

  chat.insertAdjacentHTML("beforeend", msg);
  chat.scrollTop += 500;
}

window.addEventListener("load", function () {
  const maxWidth = 50;
  const maxHeight = 50;
  const groupsDivOrig = $("#groups");
  const invitesDivOrig = $("#invites");
  const colors = ["#69B3E7", "#ddd"];

  var account = localStorage.getItem("_account");
  account = atob(account);
  account = JSON.parse(account);

  const user_id = account.userId;
  const first_name = account.firstName;
  console.log("FIRST NAME " + first_name);
  // callProfilePostApi(user_id);

  var features = localStorage.getItem("_userFeatures");
  features = atob(features);
  features = JSON.parse(features);

  console.log(JSON.stringify(features));

  var groups = localStorage.getItem("_userGroups");
  groups = atob(groups);
  groups = JSON.parse(groups);
  console.log(JSON.stringify(groups));

  var invites = localStorage.getItem("_userInvites");
  invites = atob(invites);
  invites = JSON.parse(invites);
  console.log(JSON.stringify(invites));

  console.log("THIS IS THE USER ID: " + user_id);
  var index = 0;

  groups.forEach((group) => {
    var groupId = group.groupId;
    var groupLeader = group.groupLeader;
    var groupMembers = group.groupMembers;
    console.log(groupId + ": " + groupLeader + ": " + groupMembers);

    var groupDiv = document.createElement("div");
    groupDiv.setAttribute("class", "group");
    groupDiv.innerHTML = "Group " + groupId;
    groupDiv.setAttribute("onclick", "openGroupTab('group" + groupId + "Details')");
    groupDiv.style = "background:" + colors[index % 2];
    groupDiv.style.padding = "10px";
    groupDiv.style.fontSize = "20px";
    groupDiv.style.color = colors[(index + 1) % 2];

    // Tab that is opened when groupDiv is clicked
    var groupDetails = document.createElement("div");
    groupDetails.setAttribute("class", "groupDetails");
    groupDetails.setAttribute("id", "group" + groupId + "Details");
    groupDetails.setAttribute("data-groupLeaderId", groupLeader.userId);
    groupDetails.setAttribute("data-groupId", groupId);
    groupDetails.style.display = "none";
    groupDetails.innerHTML = "Group Leader: " + groupLeader.userName + "<br>Group Members: <br>";
    for (let i = 0; i < groupMembers.length; i++) {
      groupDetails.innerHTML += groupMembers[i].userName + "<br>";
      groupDetails.style = "background:" + colors[i % 2];
      groupDetails.style.padding = "10px";
      groupDetails.style.fontSize = "15px";
      groupDetails.style.color = colors[(i + 1) % 2];
    }
    groupDetails.style.display = "none";

    var chatButton = document.createElement("button");
    chatButton.setAttribute("class", "chatButton");
    chatButton.innerHTML = "Chat";
    chatButton.style = "background:" + colors[(index + 1) % 2];
    chatButton.style.padding = "10px";
    chatButton.style.fontSize = "15px";
    chatButton.style.color = colors[index % 2];

    chatButton.setAttribute(
      "onclick",
      "openChatWindow(parentElement.getAttribute('data-groupId'), '" + user_id + "', '" + first_name + "')"
    );

    groupDetails.appendChild(chatButton);

    var deleteButton = document.createElement("button");
    deleteButton.setAttribute("class", "deleteButton");
    deleteButton.innerHTML = "Delete Group";
    deleteButton.style = "background:" + colors[(index + 1) % 2];
    deleteButton.style.padding = "10px";
    deleteButton.style.fontSize = "15px";
    deleteButton.style.color = colors[index % 2];

    deleteButton.setAttribute(
      "onclick",
      "callGroupPutApi(" +
        user_id +
        ", parentElement.getAttribute('data-groupLeaderId'), parentElement.getAttribute('data-groupId'))"
    );
    groupDetails.appendChild(deleteButton);

    groupsDivOrig.append(groupDiv);
    groupsDivOrig.append(groupDetails);
    index++;
  });
  invites.forEach((invite) => {
    var invitingGroup = invite.invitingGroup;
    if (!(Object.keys(invitingGroup).length === 0 && invitingGroup.constructor === Object)) {
      console.log("INVITE: " + JSON.stringify(invite));
      var invitee = invite.invitee;
      console.log(invitingGroup + ": " + invitee);

      var inviteDiv = document.createElement("div");
      inviteDiv.setAttribute("class", "invite");
      inviteDiv.innerHTML = "Invite from " + invitingGroup.groupLeader.userName;
      inviteDiv.setAttribute("onclick", "openInviteTab('invite" + invitingGroup.groupId + "Details')");
      inviteDiv.style = "background:" + colors[index % 2];
      inviteDiv.style.padding = "10px";
      inviteDiv.style.fontSize = "20px";
      inviteDiv.style.color = colors[(index + 1) % 2];

      // Tab that is opened when inviteDiv is clicked
      var inviteDetails = document.createElement("div");
      inviteDetails.setAttribute("class", "inviteDetails");
      inviteDetails.setAttribute("id", "invite" + invitingGroup.groupId + "Details");
      inviteDetails.setAttribute("data-invitingGroupId", invitingGroup.groupId);
      inviteDetails.setAttribute("data-inviteeId", invitee.userId);
      inviteDetails.style.display = "none";
      inviteDetails.innerHTML =
        "Inviting Group Leader: " + invitingGroup.groupLeader.userName + "<br>Inviting Group Members: <br>";
      for (let i = 0; i < invitingGroup.groupMembers.length; i++) {
        inviteDetails.innerHTML += invitingGroup.groupMembers[i].userName + "<br>";
        inviteDetails.style = "background:" + colors[i % 2];
        inviteDetails.style.padding = "10px";
        inviteDetails.style.fontSize = "15px";
        inviteDetails.style.color = colors[(i + 1) % 2];
      }
      inviteDetails.style.display = "none";

      var acceptButton = document.createElement("button");
      acceptButton.setAttribute("class", "acceptButton");
      acceptButton.innerHTML = "Accept Invitation";
      acceptButton.style = "background:" + colors[(index + 1) % 2];
      acceptButton.style.padding = "10px";
      acceptButton.style.fontSize = "15px";
      acceptButton.style.color = colors[index % 2];

      acceptButton.setAttribute(
        "onclick",
        "callRespondToInvitationPostApi({accept: 1, user_id: parentElement.getAttribute('data-inviteeId'), accepted_inv_id: parentElement.getAttribute('data-invitingGroupId')})"
      );

      var rejectButton = document.createElement("button");
      rejectButton.setAttribute("class", "rejectButton");
      rejectButton.innerHTML = "Reject Invitation";
      rejectButton.style = "background:" + colors[(index + 1) % 2];
      rejectButton.style.padding = "10px";
      rejectButton.style.fontSize = "15px";
      rejectButton.style.color = colors[index % 2];

      rejectButton.setAttribute(
        "onclick",
        "callRespondToInvitationPostApi({accept: 0, user_id: parentElement.getAttribute('data-inviteeId'), accepted_inv_id: parentElement.getAttribute('data-invitingGroupId')})"
      );

      inviteDetails.appendChild(acceptButton);
      inviteDetails.appendChild(rejectButton);

      invitesDivOrig.append(inviteDiv);
      invitesDivOrig.append(inviteDetails);
      index++;
    }
  });

  // Add chat functionality
  var chatMain = document.getElementById("chatMain");
  var chatInput = document.getElementById("chatInput");
  var chatText = document.getElementById("chatText");
  chatInput.addEventListener("submit", (event) => {
    event.preventDefault();
    const msgText = chatText.value;
    console.log("msgText: " + msgText);
    if (!msgText) return;
    var chatLogs = callChatPostApi(1, chatMain.getAttribute("data-groupId"), user_id, msgText);
    console.log("LOGS: " + JSON.stringify(chatLogs));
    speak("Me", "right", msgText);
    chatText.value = "";
  });

  // Add make group functionality
  var makeGroupButton = document.getElementById("makeGroupButton");
  makeGroupButton.setAttribute("onclick", "callGroupPostApi(" + user_id + ", [" + user_id + "])");
});
