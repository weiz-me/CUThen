const matches = {
  data: {
    compatibleUsers: [
      {
        userId: 2,
        userName: "user2",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "2Value 1" },
          { featureName: "Feature 2", featureValue: "2Value 2" },
          { featureName: "Feature 3", featureValue: "2Value 3" },
          { featureName: "Feature 4", featureValue: "2Value 4" },
          { featureName: "Feature 5", featureValue: "2Value 5" },
        ],
      },
      {
        userId: 3,
        userName: "user3",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "3Value 1" },
          { featureName: "Feature 2", featureValue: "3Value 2" },
          { featureName: "Feature 3", featureValue: "3Value 3" },
        ],
      },
      {
        userId: 4,
        userName: "user4",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "4Value 1" },
          { featureName: "Feature 2", featureValue: "4Value 2" },
          { featureName: "Feature 3", featureValue: "4Value 3" },
        ],
      },
      {
        userId: 5,
        userName: "user5",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "5Value 1" },
          { featureName: "Feature 2", featureValue: "5Value 2" },
          { featureName: "Feature 3", featureValue: "5Value 3" },
        ],
      },
      {
        userId: 6,
        userName: "user6",
        userFeatures: [
          { featureName: "Feature 1", featureValue: "6Value 1" },
          { featureName: "Feature 2", featureValue: "6Value 2" },
          { featureName: "Feature 3", featureValue: "6Value 3" },
        ],
      },
    ],
  },
};

var sdk = apigClientFactory.newClient({});

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
    //   return [1, 2, 3];
  });
}

function callMatchesPostApi(user_id) {
  params = {};
  body = { userId: user_id };
  additionalParams = {};
  sdk.matchmakerPost(params, body, additionalParams).then((response) => {
    console.log(JSON.stringify(response));
    return response;
  });
}

function showPrompt(inviteeId, inviteeName, ledGroups) {
  let groupsString = ledGroups[0];
  for (let i = 1; i < ledGroups.length; i++) {
    groupsString += ", " + ledGroups[i];
  }
  while (true) {
    let invitingGroup = prompt(
      "Enter the group ID you want to invite " + inviteeName + " to. Here are your options: " + groupsString + "."
    );
    console.log(JSON.stringify(ledGroups));
    if (ledGroups.includes(Number(invitingGroup))) {
      let message = "You have invited " + inviteeName + " to group " + invitingGroup;
      callExtendInvitationPostApi({ invitee: inviteeId, currentGroup: Number(invitingGroup) });
      alert(message);
      console.log(message);
      return Number(invitingGroup);
    }
    if (invitingGroup == null) {
      let message = "You have cancelled the invitation.";
      alert(message);
      console.log(message);
      return -1;
    }
    alert("Invalid group ID! Please try again.");
  }
}

function callExtendInvitationPostApi(out_invitation) {
  console.log("Invitation Extended to " + out_invitation.invitee + " for group " + out_invitation.currentGroup + ".");
  params = {};
  body = { o_inv: out_invitation };
  additionalParams = {};
  var response = sdk.extendInvitationPost(params, body, additionalParams);
  console.log("Response: " + response);
  return response;
  // return "Invitation Extended to " + out_invitation.invitee + " for group " + out_invitation.currentGroup + ".";
}

function showHiddenFeatures(hiddenFeatures) {
  var i, x;
  x = document.getElementsByClassName("hidden_feature");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  for (i = 0; i < hiddenFeatures.length; i++) {
    document.getElementById(hiddenFeatures[i]).style.display = "block";
  }
}

window.addEventListener("load", async function () {
  //EDIT THIS TO GET THE USER'S REPRESENTATIVE VECTOR
  const grid = document.getElementById("grid");

  // Save user_id to local storage
  const user_id = "2";
  var account = { userId: user_id };
  account = btoa(JSON.stringify(account));
  localStorage.setItem("_account", account);
  callProfilePostApi(user_id);

  // send the message to API
  var response = callMatchesPostApi(user_id);
  console.log(response);
  var compats = response.data.compatibleUsers;
  var ledGroups = JSON.parse(atob(localStorage.getItem("_ledGroups")));
  if (compats && compats.length > 1) {
    //console.log('received ' + (compats.length - 1) + ' matches');
    var displaySet = new Set();
    for (let i = 0; i < compats.length; i++) {
      if (displaySet.has(compats[i].userId)) {
        continue;
      } else {
        var item = document.createElement("div");
        item.setAttribute("data-user-id", compats[i].userId);
        item.setAttribute("grid-column", (i % 3) + " / span 1");
        item.setAttribute("grid-row", Math.floor(i / 3) + " / span 1");
        item.setAttribute("class", "grid-item");
        item.innerHTML = compats[i].userName;

        // Add button to grid-item
        var button = document.createElement("button");
        button.setAttribute("class", "extend-button");
        button.setAttribute(
          "onclick",
          "showPrompt(" +
            compats[i].userId +
            "," +
            '"' +
            compats[i].userName +
            '"' +
            "," +
            JSON.stringify(ledGroups) +
            ")"
        );
        button.innerHTML = "Extend Invitation";

        // Display text in grid-item
        const hiddenFeatures = [];
        for (let j = 0; j < compats[i].userFeatures.length; j++) {
          var feature = document.createElement("div");
          feature.innerHTML +=
            compats[i].userFeatures[j].featureName + ": " + compats[i].userFeatures[j].featureValue + "<br>";
          feature.setAttribute("class", "feature");
          feature.setAttribute("id", compats[i].userId + "feature" + j);
          // Hide features after the first two
          if (j > 1) {
            feature.setAttribute("class", "hidden_feature");
            feature.style.display = "none";
            hiddenFeatures.push(feature.id);
          }
          item.appendChild(feature);
          item.setAttribute("onclick", "showHiddenFeatures(" + JSON.stringify(hiddenFeatures) + ")");

          if (j == compats[i].userFeatures.length - 1) {
            feature.appendChild(button);
          }
        }

        grid.appendChild(item);
        displaySet.add(compats[i].userId);
      }
    }
  } else {
    var item = document.createElement("div");
    item.setAttribute("grid-column", ((i - 1) % 3) + " / span 1");
    item.setAttribute("grid-row", Math.floor((i - 1) / 3) + " / span 1");
    item.setAttribute("class", "grid-item");
    item.innerHTML = "Empty";
    grid.appendChild(item);
  }
});
