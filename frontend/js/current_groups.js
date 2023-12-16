//UNCOMMENT RELEVANT LINES WHEN API IS READY

//var sdk = apigClientFactory.newClient({});

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

function callProfileGetApiForGroupsAndInvites(user_id) {
  // Should return an object containing user groups, name, features, and pending invites
  // const userInfo = sdk.profileGet({ UserId: user_id });
  // return [userInfo.data.groups, userInfo.data.pendingInvites];
  return [groups, invites];
}

function callGroupDeleteApi(user_id, group_leader_id, group_id) {
  if (user_id == group_leader_id) {
    // return sdk.groupDelete({ GroupId: group_id });
    console.log("Group Deleted");
    return "Group Deleted";
  }
  console.log("You cannot delete this group because you are not the group leader");
  return "You cannot delete this group because you are not the group leader";
}

function callGroupPostApi(user_id, group_members) {
  if (user_id === group_leader_id) {
    for (let i = 0; i < group_members.length; i++) {
      out_invitation = { invitee: group_members[i], currentGroup: group_id };
      callExtendInvitationPostApi(out_invitation);
    }
    // return sdk.groupPost({ groupLeader: user_id, groupMembers: group_members });
    console.log("Group Created");
    return "Group Created";
  }
  console.log("You cannot create this group because you are not the group leader");
  return "You cannot edit this group because you are not the group leader";
}

function callRespondToInvitationPostApi(invitationResponse) {
  // return sdk.respondToInvitationPost({ response: invitationResponse });
  var response = invitationResponse.response;
  var inviteeId = invitationResponse.inviteeId;
  var invitingGroupId = invitationResponse.invitingGroupId;
  console.log("Responded " + response + " to Invitation");
  return "Responded " + response + " to Invitation";
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

window.addEventListener("load", function () {
  const maxWidth = 50;
  const maxHeight = 50;
  const groupsDivOrig = $("#groups");
  const invitesDivOrig = $("#invites");
  const colors = ["#69B3E7", "#ddd"];

  var account = localStorage.getItem('_account');
  account = atob(account);
  account = JSON.parse(account);

  const user_id = account.userId;
  console.log("THIS IS THE USER ID: " + user_id);
  var groupsAndInvites = callProfileGetApiForGroupsAndInvites(user_id);
  var groups = groupsAndInvites[0];
  var invites = groupsAndInvites[1];
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

    var deleteButton = document.createElement("button");
    deleteButton.setAttribute("class", "deleteButton");
    deleteButton.innerHTML = "Delete Group";
    deleteButton.style = "background:" + colors[(index + 1) % 2];
    deleteButton.style.padding = "10px";
    deleteButton.style.fontSize = "15px";
    deleteButton.style.color = colors[index % 2];

    deleteButton.setAttribute(
      "onclick",
      "callGroupDeleteApi(" + user_id + ", parentElement.getAttribute('data-groupLeaderId'), parentElement.getAttribute('data-groupId'))"
    );
    groupDetails.appendChild(deleteButton);

    groupsDivOrig.append(groupDiv);
    groupsDivOrig.append(groupDetails);
    index++;
  });
  invites.forEach((invite) => {
    var invitingGroup = invite.invitingGroup;
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
      "callRespondToInvitationPostApi({response: 'yes', inviteeId: parentElement.getAttribute('data-inviteeId'), invitingGroupId: parentElement.getAttribute('data-invitingGroupId')})"
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
      "callRespondToInvitationPostApi({response: 'no', inviteeId: parentElement.getAttribute('data-inviteeId'), invitingGroupId: parentElement.getAttribute('data-invitingGroupId')})"
    );

    inviteDetails.appendChild(acceptButton);
    inviteDetails.appendChild(rejectButton);

    invitesDivOrig.append(inviteDiv);
    invitesDivOrig.append(inviteDetails);
    index++;
  });
});
